import requests
from flask import Blueprint, render_template, request, redirect

from src.services.payment_service import generate_sign_for_payment

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
            'amount': request.form.get('amount', ''),
            'shop_id' : shop_id,
            'shop_order_id': '101',
            'description': request.form.get('description', '')
        }
        sign = generate_sign_for_payment([data['amount'],
                                        data['currency'],
                                        data['shop_id'],
                                        data['shop_order_id']])
        data['sing'] = sign
        #resp = requests.post('https://pay.piastrix.com/ru/pay', data=data)
        return render_template('pay.html', data = data)