from pathlib import Path

BASE_DIR = Path(__file__).resolve(strict=True).parent.parent


class Config(object):
    SECRET_KEY = 'you-will-never-guess'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///' + str(BASE_DIR / 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # TEMPLATE_FOLDER = str(BASE_DIR / 'templates')
