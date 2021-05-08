from logging import error
import requests
from flask import Blueprint, render_template, request, redirect, flash

from src.services.payment_service import generate_sign_for_payment
from src import logger

payments = Blueprint('payments', __name__)
shop_id = '5' 
payway = 'advcash_rub'


@payments.route('/')
def index():
    return render_template('index.html')

@payments.route('/pay', methods=['POST','GET'])
def process_payment():
    currency = request.form.get('currency', '')
    if currency == '978':
        data = {
            'currency' : currency,
            'amount': str(float(request.form.get('amount', ''))),
            'shop_id' : shop_id,
            'shop_order_id': '101',
            'description': request.form.get('description', '')
        }
        sign = generate_sign_for_payment([data['amount'],
                                        data['currency'],
                                        data['shop_id'],
                                        data['shop_order_id']])
        data['sign'] = sign
        logger.info(f"Currency: {data['currency']}, Amount:{data['amount']}, Description {data['description']}")
        return render_template('pay.html', data = data, url = 'https://pay.piastrix.com/ru/pay',
                                method = 'POST')
                                
    elif currency == '840':
        data = {
            'payer_currency' : int(currency),
            'shop_currency' : int(currency),
            'shop_amount': str(float(request.form.get('amount', ''))),
            'shop_id' : shop_id,
            'shop_order_id': 101,
            'description': request.form.get('description', '')
        }
        sign = generate_sign_for_payment([data['payer_currency'],
                                        data['shop_amount'],
                                        data['shop_currency'],
                                        data['shop_id'],
                                        data['shop_order_id']
                                        ])
        data['sign'] = sign
        resp = requests.post('https://core.piastrix.com/bill/create', json = data,
                            headers={'Content-Type': 'application/json'})  
        logger.info(f"Currency: {data['shop_currency']}, Amount:{data['shop_amount']}, Description {data['description']}")
        return redirect(resp.json()['data']['url'])

    elif currency == '643':
        data = {
            'currency' : int(currency),
            'payway' : payway,
            'amount' : str(float(request.form.get('amount', ''))),
            'shop_id' : shop_id,
            'shop_order_id': 101,
            'description': request.form.get('description', '')
        }
        sign = generate_sign_for_payment([data['amount'],
                                        data['currency'],
                                        data['payway'],
                                        data['shop_id'],
                                        data['shop_order_id']
                                        ])
        data['sign'] = sign
        resp = requests.post('https://core.piastrix.com/invoice/create', json = data,
                            headers={'Content-Type': 'application/json'})
        logger.info(f"Currency: {data['currency']}, Amount:{data['amount']}, Description {data['description']}")
        return render_template('pay.html', data = resp.json()['data']['data'],
                                method = resp.json()['data']['method'],
                                url = resp.json()['data']['url'], )
    return render_template('index.html') 

