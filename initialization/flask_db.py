from db import get_config_uri, FLASK_DB, APP_SQLALCHEMY_ENGINE_OPTIONS


def init_flask_db(app):
    """
    Main entry point of the module.

    Initializes Flask-SQLAlchemy. We do not follow the recommended approach in
    the Flask-SQLAlchemy documentation, we manage the database connection
    through a global record that is assigned in a callback in the
    ``global_handlers`` initializer.

    Most of the actual core database code is in the ``db`` module at the root
    of the application.
    """

    app.config["SQLALCHEMY_DATABASE_URI"] = get_config_uri()
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = APP_SQLALCHEMY_ENGINE_OPTIONS

    FLASK_DB.init_app(app)

    return app
