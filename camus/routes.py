import asyncio
import logging
import json 

import sqlalchemy
from quart import (Blueprint, copy_current_websocket_context, flash, redirect,
                   render_template, session, websocket, request, jsonify)

from camus import db
from camus.forms import OrderForm
from camus.models import Orders
from camus.logic import redirecter
from camus.util import commit_database
import aiohttp 

bp = Blueprint('main', __name__)


@bp.route('/about')
async def about():
    async with aiohttp.ClientSession() as session:
        async with session.get('http://ifconfig.me') as response:

            print("Status:", response.status)

            html = await response.text()
    return html


async def redirect_pay(request_params:dict):
    if request_params['_method_order'].lower() == 'pay':
        return await render_template('order_redirect.html',
                request_params=request_params, code=307)
   
    elif (request_params['_method_order'].lower() == 'bill' or 
          request_params['_method_order'].lower() == 'invoice'):
        header = {'Content-Type': 'application/json'}
        post_params = {k: v for k, v in request_params.items() if not k.startswith('_')}
        async with aiohttp.ClientSession() as session:
            async with session.post(request_params['_redirect_url'], json=post_params, headers=header) as r:

                print("Status:", r.status)
                try:
                    res = await r.json()
                except:
                    res = await r.text()
        print(request_params['_redirect_url'])
        print(post_params)
        print(header)
        print(res)
        
        if request_params['_method_order'].lower() == 'bill':
            print(res['data']['url'])
            return redirect(res['data']['url'])
        
        elif request_params['_method_order'].lower() == 'invoice':
            print(res['data']['url'])
            post_params = {}
            for k, v in res['data']['data'].items():
                post_params[k] = v
            for k, v in res['data'].items():
                if k != 'data':
                    post_params[k] = v
            return await render_template('invoice_redirect.html',
                request_params=post_params, code=307)
            
        return res
    
                
                

@bp.route('/', methods=['GET', 'POST'])
async def index():
    price_form = OrderForm()
    if price_form.validate_on_submit():
        form = price_form
        price = form.price.data
        currency = form.currency.data
        description = form.description.data
        # with open(r"C:\Users\logs", 'a') as f:
            # f.write(f' {price} {currency} {description} ')

        try:
            order = Orders(price=price, currency=currency, description=description)
            db.session.add(order)
            commit_database(reraise=True)
            request_params = redirecter({'price':price, 
                                        'currency':currency, 'description':description})
        
            
            return await redirect_pay(request_params)
            
        except sqlalchemy.exc.IntegrityError:
            await flash('The room name "{}" is not available')

    return await render_template(
        'index.html', price_form=price_form)


@bp.route('/create_room', methods=['POST'])
async def new_room():
    request_ =  request.args
    print(request_)
    # input_data = json.loads(request_)

    # if create_room_form.validate_on_submit():
    # form = create_room_form
    name = request_.get('room_name')
    password = request_.get('password')
    is_public = request_.get('public')
    if is_public:
        is_public = True
    guest_limit = request_.get('guest_limit')

    try:
        room = Room(guest_limit=guest_limit, is_public=is_public)
        room.set_name(name)
        if password:
            room.set_password(password)
        db.session.add(room)
        commit_database(reraise=True)

        url_to_redirect = f'/room/{room.slug}'
        out_data =  {'name': name, 'password':password, 'is_public': is_public, 'guest_limit': guest_limit}
        return jsonify(out_data)
        # return redirect('/room/{}'.format(room.slug), code=307)
    except sqlalchemy.exc.IntegrityError:
        return jsonify(f'The room name "{name}" is not available')



# The `/chat` route is deprecated.
# @bp.route('/chat')
# async def chat_index():
#     return redirect('/', code=307)


# The `/chat/` route is deprecated. Prefer`/room/` instead.
# @bp.route('/chat/<room_id>', methods=['GET', 'POST'])
@bp.route('/room/<room_id>', methods=['GET', 'POST'])
async def room(room_id):
    room = Room.query.filter_by(slug=room_id).first_or_404()

    if room.is_full():
        return 'Guest limit already reached', 418

    # No password is required to join the room
    client = room.authenticate()
    if client:
        db.session.add(client)
        commit_database(reraise=True)
        session['id'] = client.uuid

        return await render_template(
            'chatroom.html', title='Camus | {}'.format(room.name))

    # A password is required to join the room
    status_code = 200
    form = JoinRoomForm()
    if form.validate_on_submit():
        password = form.password.data

        client = room.authenticate(password)
        if client:
            db.session.add(client)
            commit_database(reraise=True)
            session['id'] = client.uuid

            return await render_template(
                'chatroom.html', title='Camus | {}'.format(room.name))

        # Authentication failed
        status_code = 401
        await flash('Invalid password')

    return (
        (await render_template('join-room.html', title='Camus | Join a room',
                               form=form, room=room)),
        status_code)


@bp.route('/chat/<room_id>', methods=['POST'])
async def chat(room_id):
    room = Room.query.filter_by(slug=room_id).first_or_404()

    if room.is_full():
        return 'Guest limit already reached', 418

    # No password is required to join the room
    client = room.authenticate()
    if not client:
        status_code = 200
        password = request.args.get('password')
        client = room.authenticate(password)

    if client:
        db.session.add(client)
        commit_database(reraise=True)
        session['id'] = client.uuid

        return f'user added to {room.name}', 200

    else:
        # Authentication failed
        status_code = 401
        return 'Invalid password', 401



# The `/chat/` route is deprecated. Prefer`/room/` instead.
@bp.websocket('/room/<room_id>/ws')
async def room_ws(room_id):
    # Verify that the room exists
    Room.query.filter_by(slug=room_id).first_or_404()

    # Verify the client using a secure cookie
    client = Client.query.filter_by(uuid=session.get('id', None)).first()
    if client:
        logging.info(f'Accepted websocket connection for client {client.uuid}')
        await websocket.accept()
    else:
        return 'Forbidden', 403

    inbox, outbox = message_handler.inbox, message_handler.outbox

    send_task = asyncio.create_task(
        copy_current_websocket_context(ws_send)(outbox[client.uuid]),
    )
    receive_task = asyncio.create_task(
        copy_current_websocket_context(ws_receive)(client.uuid, inbox),
    )
    try:
        await asyncio.gather(send_task, receive_task)
    finally:
        logging.info(f'Terminating websocket connection for client {client.uuid}')
        send_task.cancel()
        receive_task.cancel()



# The `/chat/` route is deprecated. Prefer`/room/` instead.
@bp.websocket('/chat/<room_id>/ws')
async def chat_ws(room_id):
    # Verify that the room exists
    Room.query.filter_by(slug=room_id).first_or_404()

    # Verify the client using a secure cookie
    client = Client.query.filter_by(uuid=session.get('id', None)).first()
    if client:
        logging.info(f'Accepted websocket connection for client {client.uuid}')
        await websocket.accept()
    else:
        return 'Forbidden', 403

    inbox, outbox = message_handler.inbox, message_handler.outbox

    send_task = asyncio.create_task(
        copy_current_websocket_context(ws_send)(outbox[client.uuid]),
    )
    receive_task = asyncio.create_task(
        copy_current_websocket_context(ws_receive)(client.uuid, inbox),
    )
    try:
        await asyncio.gather(send_task, receive_task)
    finally:
        logging.info(f'Terminating websocket connection for client {client.uuid}')
        send_task.cancel()
        receive_task.cancel()


@bp.route('/public')
async def public():
    public_rooms = Room.query.filter_by(is_public=True).all()

    return await render_template(
        'public.html', title='Camus Video Chat | Public Rooms',
        public_rooms=public_rooms)


@bp.route('/public_api', methods=['POST'])
async def public_api():
    public_rooms = Room.query.filter_by(is_public=True).all()
    # j = json.dumps(public_rooms)
    rooms = {}
    for room in public_rooms:
        if room.clients:
            clients = {}
            for client in room.clients: 
                clients[client.id] = {
                    'name': client.name, 'uuid': client.uuid,
                    'seen': client.seen, 'room_id': client.room_id
                                     }
        else:
            clients = {}
        
        room_dict = {
            'room_name':room.name, 'slug':room.slug, 
            'guest_limit':room.guest_limit, 'is_public':room.is_public,
            'is_active':room.active, 'clients': clients
                    }
        rooms[room.id] = room_dict

    return rooms





async def ws_send(queue):
    while True:
        message = await queue.get()
        await websocket.send(message)


async def ws_receive(client_id, queue):
    while True:
        message = await websocket.receive()
        await queue.put((client_id, message))
