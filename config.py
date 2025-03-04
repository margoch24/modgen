import os
from datetime import timedelta

from dotenv import load_dotenv

from api.constants import Environment

load_dotenv()


def get_dotenv_val(name):
    return os.environ.get(name)


class DefaultConfig:
    SINGLE_TEST = get_dotenv_val("ONLY")
    PORT = get_dotenv_val("PORT")
    ENV = get_dotenv_val("ENV")
    DATABASE_URI = get_dotenv_val("DATABASE_URI")
    TEST_DATABASE_URI = get_dotenv_val("TEST_DATABASE_URI")
    APP_TOKEN = get_dotenv_val("APP_TOKEN")
    FRONTEND_API_URL = get_dotenv_val("FRONTEND_API_URL")
    UPLOAD_FOLDER = "uploads"
    ALLOWED_EXTENSIONS = ["png", "jpg", "jpeg"]


class FlaskAppConfig:
    DEBUG = get_dotenv_val("FLASK_DEBUG")
    SECRET_KEY = get_dotenv_val("SECRET_KEY")
    UPLOAD_FOLDER = DefaultConfig.UPLOAD_FOLDER

    SQLALCHEMY_ECHO = get_dotenv_val("FLASK_SQLALCHEMY_ECHO")
    SQLALCHEMY_TRACK_MODIFICATIONS = get_dotenv_val(
        "FLASK_SQLALCHEMY_TRACK_MODIFICATIONS"
    )
    SQLALCHEMY_DATABASE_URI = (
        DefaultConfig.TEST_DATABASE_URI
        if DefaultConfig.ENV == Environment.TEST
        else DefaultConfig.DATABASE_URI
    )
