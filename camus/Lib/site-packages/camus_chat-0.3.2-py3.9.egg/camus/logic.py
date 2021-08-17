

from quart.utils import redirect
from uuid import uuid4


SHOP_ID = 5 
SECRET_KEY = 'SecretKey01'
PAYWAY = 'advcash_rub'
CURRENCY = {'usd': 840, 'rub': 643, 'eur': 978} #978
SHOP_ORDER_ID = 101
PARAMS = {'pay': ['amount', 'currency', 'shop_id', 'shop_order_id'],
          'bill': ['shop_amount', 'shop_currency', 'shop_id', 'shop_order_id', 'payer_currency'],
          'invoice': ['amount', 'currency', 'payway', 'shop_id', 'shop_order_id']
         }


def sort_param(method:str):
    params_sort = globals()['PARAMS'][method]
    params_sort.sort()
    return params_sort


def adder_params(method:str, order:dict):
    sign_param = {}
    currency = globals()['CURRENCY'][order['currency'].lower()]
    if method == 'pay':
        sign_param['amount'] = order['price']
        sign_param['currency'] = currency
        sign_param['shop_id'] = globals()['SHOP_ID']
        sign_param['shop_order_id'] = globals()['SHOP_ORDER_ID']
    if method == 'bill':
        sign_param['shop_amount'] = order['price']
        sign_param['shop_currency'] = currency
        sign_param['shop_id'] = globals()['SHOP_ID']
        sign_param['shop_order_id'] = globals()['SHOP_ORDER_ID'] #uuid4()
        sign_param['payer_currency'] = currency
    if method == 'invoice':
        sign_param['amount'] = order['price']
        sign_param['currency'] = currency
        sign_param['payway'] = globals()['PAYWAY']
        sign_param['shop_id'] = globals()['SHOP_ID']
        sign_param['shop_order_id'] = globals()['SHOP_ORDER_ID']
    sign, unsign = signer(method, sign_param)
    request_param = sign_param
    request_param['sign'] = sign
    request_param['_unsign'] = unsign
    request_param['description'] = order['description']    
    return request_param
    
    
def signer(method:str, sign_param:dict):
    params_sort = sort_param(method) 
    sign_str = ''
    for param in params_sort:
        sign_str += str(sign_param[param])
        sign_str += ':'
    sign_str = sign_str[:-1]
    sign_str += globals()['SECRET_KEY']
    import hashlib
    hash_ = hashlib.sha256(sign_str.encode())
    hash_hex = hash_.hexdigest()
    return hash_hex, sign_str
    

# def prepare_to_jinja(request_params:dict):
#     reuest_params_jinja = {}
#     for param, value in request_params.items():
#         reuest_params_jinja[param] = 
    
    
def redirecter(order:dict):
    currency = order['currency'].upper()
    if currency == 'EUR':
        redirect_url = 'https://pay.piastrix.com/ru/pay'
        method_order = 'pay'
    elif currency == 'USD':
        redirect_url = 'https://core.piastrix.com/bill/create'
        method_order = 'bill'
    elif currency == 'RUB':
        redirect_url = 'https://core.piastrix.com/invoice/create'
        method_order = 'invoice'
    request_param =  adder_params(method_order, order)
    request_param['_redirect_url'] = redirect_url
    request_param['_method_order'] = method_order.capitalize()
    # request_param = prepare_to_jinja(request_param)
    
    return request_param