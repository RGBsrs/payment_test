import datetime
import requests
from flask import Blueprint, render_template, request, redirect

from src import logger, db
from src.services.payment_service import generate_sign_for_payment, payment_logger
from src.database.models import Payment

payments = Blueprint('payments', __name__)
shop_id = '5' 
payway = 'advcash_rub'


@payments.route('/')
def index():
    return render_template('index.html')

@payments.route('/pay', methods=['POST','GET'])
def process_payment():
    currency = request.form.get('currency', '')
    if request.form.get('amount', '') == '':
        return render_template('index.html', message = 'Введите сумму')
    if currency == '643' and float(request.form.get('amount', '')) < 10.0:
        return render_template('index.html', message = 'Введите сумму не меньше 10.0 RUB')
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
        try:
            payment = Payment(currency_id = int(data['currency']),
                                amount = float(data['amount']),
                                description = data['description'])
            db.session.add(payment)
            db.session.flush()
            payment_logger(f"Time: {datetime.datetime.now()}, Currency: {data['currency']},Amount:{data['amount']}, Description {data['description']}, payment_id: {payment.id}")
            db.session.commit()
            return render_template('pay.html', data = data, url = 'https://pay.piastrix.com/ru/pay',
                                    method = 'POST')
        except Exception as e: 
            logger.error(e)
            return render_template('index.html', message = 'Упс, что-то пошло не так.')
                                
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
        try:    
            payment = Payment(currency_id = int(data['payer_currency']),
                                    amount = float(data['shop_amount']),
                                    description = data['description'])
            db.session.add(payment)
            db.session.flush()
            resp = requests.post('https://core.piastrix.com/bill/create', json = data,
                                headers={'Content-Type': 'application/json'})  
            payment_logger(f"Time: {datetime.datetime.now()},Currency: {data['shop_currency']}, Amount:{data['shop_amount']}, Description {data['description']}, payment_id: {payment.id}")
            return redirect(resp.json()['data']['url'])
        except Exception as e:
            logger.error(e)
            return render_template('index.html', message = 'Упс, что-то пошло не так.')

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
        payment = Payment(currency_id = int(data['currency']),
                                amount = float(data['amount']),
                                description = data['description'])
        try:
            db.session.add(payment)
            db.session.flush()
            payment_logger(f"Time: {datetime.datetime.now()},Currency: {data['currency']},Amount:{data['amount']}, Description {data['description']}, payment_id: {payment.id}")
            db.session.commit()
            resp = requests.post('https://core.piastrix.com/invoice/create', json = data,
                                headers={'Content-Type': 'application/json'})
            return render_template('pay.html', data = resp.json()['data']['data'],
                                    method = resp.json()['data']['method'],
                                    url = resp.json()['data']['url'], )
        except Exception as e:
            logger.error(e)
            return render_template('index.html', message = 'Упс, что-то пошло не так.')
    return render_template('index.html', message = 'Выберите валюту') 

