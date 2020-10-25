from flask import Flask

from .mongodb import Mongodb


# mongodb 'global' instance
mongo = Mongodb()


def create_app(config_filename=None):
    app = Flask(__name__)
    # app.config.from_pyfile(config_filename)

    # init mongodb
    mongo.init_app(app)

    with app.app_context():
        # http routes 
        from . import routes

    return app
