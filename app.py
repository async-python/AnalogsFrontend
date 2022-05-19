from flask_bootstrap import Bootstrap4
from flask_migrate import Migrate

import flask_login
from flask import Flask
from core.config import Config
from src.ctx_processor import year_processor
from src.database import db
from src.users import load_user, handle_needs_login
from src.views import analog


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    login_manager = flask_login.LoginManager()
    login_manager.init_app(app)
    login_manager.user_loader(load_user)
    login_manager.unauthorized_handler(handle_needs_login)
    Bootstrap4(app)
    db.init_app(app)
    Migrate(app, db)
    app.context_processor(year_processor)
    app.register_blueprint(analog, url_prefix='')
    return app


if __name__ == '__main__':
    app = create_app()
    app.run()
