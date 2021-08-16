

shop_id = 5 
secretKey = 'SecretKey01'
payway = 'advcash_rub'

params = {'pay': ['amount', 'currency', 'shop_id', 'shop_order_id'],
          'bill': ['shop_amount', 'shop_currency', 'shop_id', 'shop_order_id', 'payer_currency'],
          'invoice': [' amount', 'currency', 'payway', 'shop_id', 'shop_order_id']
        }


def sort_param():
    