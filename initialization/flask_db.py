from db import get_config_uri, FLASK_DB, APP_SQLALCHEMY_ENGINE_OPTIONS


def init_flask_db(app):
    app.config["SQLALCHEMY_DATABASE_URI"] = get_config_uri()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = APP_SQLALCHEMY_ENGINE_OPTIONS

    FLASK_DB.init_app(app)

    return app
