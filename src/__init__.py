import os
import config
import logging
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate


app = Flask(__name__)
app.config.from_object(config.Config)

db = SQLAlchemy(app)
migrate = Migrate(app, db)

if not os.path.exists("src/logs/"):
    os.mkdir("src/logs/")


def setup_logger():
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.INFO)

    formatter = logging.Formatter("%(name)s:%(levelname)s \n%(message)s")
    file_handler = logging.FileHandler("src/logs/payments.log")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger


logger = setup_logger()

from src.database import models
from src.views import views

app.register_blueprint(views)
