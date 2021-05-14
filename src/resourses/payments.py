from hashlib import sha256
import random
from src import app

shop_id = "5"
payway = "advcash_rub"


class Payment:
    direct_url = "https://pay.piastrix.com/ru/pay"
    bill_url = "https://core.piastrix.com/bill/create"
    invoice_url = "https://core.piastrix.com/invoice/create"

    def __init__(self, currency_code, amount):
        self.currency_code = currency_code
        self.amount = amount

    def prepare_payment_data(self):
        if self.currency_code == "978":
            payment_data, required_fields = self._direct_payment_data()
            payment_url = self.direct_url
        elif self.currency_code == "840":
            payment_data, required_fields = self._bill_payment_data()
            payment_url = self.bill_url
        else:
            payment_data, required_fields = self._invoice_payment_data()
            payment_url = self.invoice_url
        payment_data["sign"] = self.generate_sign_for_payment(
            payment_data, required_fields
        )
        return payment_data, payment_url

    def _direct_payment_data(self):
        required_fields = ["amount", "currency", "shop_id", "shop_order_id"]
        data = {
            "currency": self.currency_code,
            "amount": self.amount,
            "shop_id": shop_id,
            "shop_order_id": random.randrange(255),
        }
        return data, required_fields

    def _bill_payment_data(self):
        required_fileds = [
            "payer_currency",
            "shop_amount",
            "shop_currency",
            "shop_id",
            "shop_order_id",
        ]
        data = {
            "payer_currency": self.currency_code,
            "shop_currency": self.currency_code,
            "shop_amount": self.amount,
            "shop_id": shop_id,
            "shop_order_id": random.randrange(255),
        }
        return data, required_fileds

    def _invoice_payment_data(self):
        required_fileds = ["amount", "currency", "payway", "shop_id", "shop_order_id"]
        data = {
            "currency": self.currency_code,
            "payway": payway,
            "amount": self.amount,
            "shop_id": shop_id,
            "shop_order_id": random.randrange(255),
        }
        return data, required_fileds

    def generate_sign_for_payment(self, data, required_fileds):
        sorted_required_fields = sorted(required_fileds)
        required_values = [str(data[k]) for k in sorted_required_fields]
        sign = ":".join(required_values)
        sign = sign + app.config["PAYMENT_KEY"]
        return sha256(sign.encode()).hexdigest()
