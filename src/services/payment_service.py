from hashlib import sha256

from src import app


def generate_sign_for_payment(params: list) -> str:
    sign = ""
    for param in params:
        sign += str(param) + ":"
    sign = sign[:-1] + app.config["PAYMENT_KEY"]
    return sha256(sign.encode("utf-8")).hexdigest()


def payment_logger(message: str) -> None:
    with open("src/logs/payments.txt", "a") as log:
        log.write(message)
    return
