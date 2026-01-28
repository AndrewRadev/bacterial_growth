import os

from dotenv import load_dotenv


def init_config(app):
    """
    Main entry point of the module.

    Some configuration comes from the ``.env`` file at the root of the
    application. The hardcoded config in this file is mostly configuration that
    will not vary across installations like turning on DEBUG mode in
    development.

    Full configuration reference: https://flask.palletsprojects.com/en/stable/config/
    """
    app_env   = os.getenv('APP_ENV', 'development')
    log_level = os.getenv('LOG_LEVEL', None)
    timing    = os.getenv('TIME')

    # Load .env file from local directory, except in test mode
    if app_env != 'test':
        load_dotenv('.env')

    # Load env variables starting with "MGROWTHDB_" into the config
    app.config.from_prefixed_env('MGROWTHDB')

    # 200MiB max size
    app.config['MAX_CONTENT_LENGTH'] = 200 * 1024 * 1024

    # Render JSON in the given order, instead of sorting:
    app.json_provider_class.sort_keys = False
    # Render μ correctly:
    app.json_provider_class.ensure_ascii = False

    if app_env == 'development':
        app.config.update(
            DEBUG=True,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=True,
            EXPLAIN_TEMPLATE_LOADING=False,
        )
    elif app_env == 'test':
        app.config.update(
            DEBUG=False,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=False,
            EXPLAIN_TEMPLATE_LOADING=False,
            WTF_CSRF_ENABLED=False,
            SECRET_KEY='testing_key',
            SERVER_NAME='',
            PREFERRED_URL_SCHEME='http://',
        )
    elif app_env == 'production':
        app.config.update(
            DEBUG=False,
            ASSETS_DEBUG=False,
            TEMPLATES_AUTO_RELOAD=False,
            EXPLAIN_TEMPLATE_LOADING=True,
            SESSION_COOKIE_SECURE=True,
        )
    else:
        raise KeyError(f"Unknown APP_ENV: {app_env}")

    if log_level:
        app.logger.setLevel(log_level.upper())

    if timing:
        app.logger.getChild('timing').setLevel('INFO')

    if ip_forwarding_levels := int(app.config.get('IP_FORWARDING', '0')):
        # In prod, we'd expect to run behind proxies, so we need to set the
        # number of these in the .env file.
        from werkzeug.middleware.proxy_fix import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app, x_for=ip_forwarding_levels)

    return app
