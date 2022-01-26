import re
import datetime
import requests

from textdistance import levenshtein
from flask import Blueprint, render_template, request, redirect, jsonify

from src import logger, db, logger
from src.resourses.payments import Payment
from src.database.models import PaymentInfo
from src.forms.payment import PaymentForm

views = Blueprint("views", __name__)


@views.route("/", methods=["POST", "GET"])
def process_payment():
    form = PaymentForm(request.form)
    if request.method == "POST" and form.validate():
        currency = form.currency.data
        amount = form.amount.data
        # currency = request.form.get("currency", "")
        # amount = request.form.get("amount", "")

        payment = Payment(str(currency), float(amount))
        fields, url = payment.prepare_payment_data()
        fields["description"] = form.description.data

        try:
            payment_info = PaymentInfo(
                currency_id=payment.currency_code,
                amount=payment.amount,
                description=fields["description"],
            )
            db.session.add(payment_info)
            db.session.flush()
            db.session.commit()
            logger.info(
                f"Time: {datetime.datetime.now()}\n"
                f"Currency: {payment.currency_code}\n"
                f"Amount:{payment.amount}\n"
                f'Description {fields["description"]}\n'
                f"payment_id: {payment_info.id}\n"
            )
        except Exception as e:
            db.session.rollback()
            logger.error(e)
            render_template("index.html", message="Упс, что-то пошло не так.")

        # USD payment
        if currency == "978":
            return render_template("pay.html", data=fields, url=url, method="POST")

        else:
            resp = requests.post(url, json=fields)
            if not resp:
                logger.info("Not connection")
                return render_template(
                    "index.html", message="Нет соединения с сервером оплаты."
                )
            if not resp.json()["result"]:
                logger.info(
                    f"Piastrix error {resp.json()['message']} : {resp.json()['error_code']}"
                )
                return render_template("index.html", message=resp.json()["message"])

            # EUR payment
            if currency == "840":
                return redirect(resp.json()["data"]["url"])

            # RUB payment
            else:
                return render_template(
                    "pay.html",
                    data=resp.json()["data"]["data"],
                    method=resp.json()["data"]["method"],
                    url=resp.json()["data"]["url"],
                )

    else:
        return render_template("index.html", form = form)


@views.route('/messages_left')
def messages_left():
    return jsonify({'messages_left':'5'}),200

@views.route('/message_compare')
def message_compare():
    message = request.get('message', '')
    author = request.get('author', '')
    if message:
        ocr_message = request.get('ocr_message', '')
        if ocr_message:
            ocr_message = re.sub("[0-9]{1}[\/,:][0-9]{2}|PM|AM", '', ocr_message)
            ocr_message = ocr_message.split(author)[-1]
            matching = levenshtein.normalized_similarity(message, ocr_message)
            return jsonify({'matching_score': str(matching),
                            'cleaned_message': ocr_message}), 200
        return jsonify({'error': 'nothing to match'}), 405
    return jsonify({'error': 'no data to match'}), 405