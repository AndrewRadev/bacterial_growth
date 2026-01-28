from uuid import uuid4
from datetime import datetime, UTC
from pathlib import Path

from flask import (
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
    current_app,
)
import sqlalchemy as sql
import sqlalchemy.exc as sql_exceptions
from crawlerdetect import CrawlerDetect
import maxminddb

from db import get_connection, FLASK_DB
from app.model.orm import (
    User,
    PageVisit
)
from app.model.lib.errors import LoginRequired

def init_global_handlers(app):
    """
    Main entry point of the module.

    Assigns a number of request callbacks and error handlers. This includes
    storing a database connection in ``g.db_session`` and fetching the
    currently logged-in user in ``g.current_user``.
    """

    maxminddb_path = Path('var/GeoLite2-Country.mmdb')
    if maxminddb_path.exists():
        try:
            setattr(app, 'maxminddb', maxminddb.open_database(maxminddb_path))
            # Note: this doesn't get a `close()` call, but we only read from
            # it, so it should be fine if the process gets killed.
        except maxminddb.InvalidDatabaseError:
            app.logger.warn(f"Maxmind DB exists, but can't be opened: {maxminddb_path}")
        except Exception as e:
            app.logger.warn(f"Error initializing maxminddb: {e}")

    app.before_request(_make_session_permanent)
    app.before_request(_set_variables)
    app.before_request(_open_db_connection)
    app.before_request(_fetch_user)
    app.before_request(_record_page_visit)

    app.after_request(_close_db_connection)

    app.errorhandler(404)(_render_not_found)
    app.errorhandler(sql_exceptions.NoResultFound)(_render_not_found)

    app.errorhandler(403)(_render_forbidden)
    app.errorhandler(500)(_render_server_error)

    app.errorhandler(LoginRequired)(_redirect_to_login)

    return app


def _make_session_permanent():
    # By default, expires in 31 days
    session.permanent = True


def _set_variables():
    if request.cookies.get('sidebar-open', 'true') == 'true':
        g.sidebar_open = True
    else:
        g.sidebar_open = False

    g.items_per_page = request.cookies.get('items-per-page', '10')
    g.now = datetime.now(UTC)


def _open_db_connection():
    if _is_static(request):
        # Ignore static files
        return

    if 'db_conn' not in g:
        g.db_conn = get_connection()

    if 'db_session' not in g:
        g.db_session = FLASK_DB.session


def _fetch_user():
    if _is_static(request):
        # Ignore static files
        return

    if 'user' not in g:
        if 'user_uuid' in session:
            user_uuid = session['user_uuid']
        else:
            # Create a new user UUID so we can keep track of this browser
            user_uuid = str(uuid4())

        session['user_uuid'] = user_uuid

        g.current_user = g.db_session.scalars(
            sql.select(User)
            .where(User.uuid == user_uuid)
            .limit(1)
        ).one_or_none()


def _record_page_visit():
    if request.method != 'GET':
        # We only track direct page visits
        return
    if _is_static(request):
        # Don't record static files
        return
    if request.path.startswith('/admin/'):
        # Ignore admin page requests
        return
    if _is_ajax(request):
        # Ignore ajax requests
        return

    country = None
    if request.remote_addr and hasattr(current_app, 'maxminddb'):
        info = None
        try:
            ip = request.remote_addr
            if ip.startswith('[') and ip.endswith(']'):
                # IPv6 addresses may be wrapped in brackets, so let's remove them
                ip = ip[1:-1]

            info = current_app.maxminddb.get(ip)
        except Exception as e:
            current_app.logger.warn(f"Maxmind Lookup failed: {e}")

        if info:
            country = info.get('country', {}).get('names', {}).get('en')

    page_visit = PageVisit(
        path=request.path,
        query=request.query_string,
        referrer=request.referrer,
        ip=request.remote_addr,
        country=country,
        userAgent=request.user_agent.string,
        uuid=session['user_uuid'],
        isUser=(True if g.current_user else False),
        isAdmin=(True if g.current_user and g.current_user.isAdmin else False),
        isBot=CrawlerDetect().isCrawler(request.user_agent.string),
    )

    g.db_session.add(page_visit)
    g.db_session.commit()


def _close_db_connection(response):
    if _is_static(request):
        # Ignore static files
        return response

    db_conn = g.pop('db_conn', None)
    if db_conn is not None:
        db_conn.close()

    return response


def _render_not_found(_error):
    if _is_json(request):
        return {'error': '404 Not found'}, 404
    if _is_csv(request):
        return '404 Not found', 404
    else:
        return render_template('errors/404.html'), 404


def _render_forbidden(_error):
    if _is_json(request):
        return {'error': '403 Forbidden'}, 403
    else:
        return render_template('errors/403.html'), 403


def _render_server_error(_error):
    if _is_json(request):
        return {'error': '500 Server error'}, 500
    else:
        return render_template('errors/500.html'), 500


def _redirect_to_login(_error):
    return redirect(url_for('user_login_page'))


def _is_json(request):
    return request.path.endswith('.json')


def _is_csv(request):
    return request.path.endswith('.csv')


def _is_static(request):
    return request.endpoint in ('static', 'admin.static', None)


def _is_ajax(request):
    return request.headers.get('X-Requested-With', '') == 'XMLHttpRequest'
