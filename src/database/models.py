import datetime
from src import db


class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    currency_id = db.Column(db.Integer, nullable=False)
    amount = db.Column(db.Float, nullable=False)
    payment_time = db.Column(db.DateTime, default=datetime.datetime.now())
    description = db.Column(db.Text)

    def __repr__(self):
        return f"Currency: ({self.currency_id}, amount: {self.amount}, timestamp = {self.payment_time})"
