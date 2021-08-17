import asyncio
import logging
import json 

import sqlalchemy
from quart import (Blueprint, copy_current_websocket_context, flash, redirect,
                   render_template, session, websocket, request, jsonify)

from app import db
from forms import OrderForm
from models import Orders
from logic import redirecter
from util import commit_database
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
