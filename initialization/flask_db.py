import simplejson as json

from db import get_config_uri, FLASK_DB, SQLALCHEMY_ENGINE_OPTIONS


def init_flask_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = get_config_uri()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = SQLALCHEMY_ENGINE_OPTIONS

    FLASK_DB.init_app(app)

    return app
