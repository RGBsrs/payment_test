from wtforms import Form, SelectField, TextAreaField, DecimalField, validators


class PaymentForm(Form):
    amount = DecimalField(
        "amount",
        [
            validators.number_range(min=0.01),
            validators.DataRequired(message="Not correct amount"),
        ],
    )
    currency = SelectField(
        "currency",
        choices=[("978", "EUR"), ("840", "USD"), ("643", "RUB")],
    )
    description = TextAreaField("description")
