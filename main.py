import os

from flask import Flask
from werkzeug.middleware.proxy_fix import ProxyFix

from initialization.config import init_config
from initialization.flask_db import init_flask_db
from initialization.assets import init_assets
from initialization.routes import init_routes
from initialization.plotly import init_plotly
from initialization.timing import init_timing
from initialization.global_handlers import init_global_handlers
from initialization.template_filters import init_template_filters
from initialization.admin import init_admin
from initialization.celery import init_celery
from initialization.dev import dump_project_metadata


def create_app():
    env = os.getenv('APP_ENV', 'development')
    app = Flask(
        __name__,
        template_folder="app/view/templates",
        static_folder="static"
    )

    app = init_config(app)
    app = init_flask_db(app)
    app = init_assets(app)
    app = init_routes(app)
    app = init_global_handlers(app)
    app = init_template_filters(app)
    app = init_admin(app)
    app = init_celery(app)

    init_plotly()

    if env == 'development' or os.getenv('TIME'):
        app = init_timing(app)

    if env == 'development':
        dump_project_metadata(app)

    if env == 'production':
        # In prod, we run behind nginx, so take its X-Forwarded-For field as
        # the remote address:
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1)

    return app


if __name__ == "__main__":
    app = create_app()

    app.run(host="0.0.0.0", port=8081)
