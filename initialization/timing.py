import os
import time

from flask import g, current_app, request
from sqlalchemy import event as sql_event
from sqlalchemy.engine import Engine


def init_timing(app):
    """
    Main entry point of the module.

    It assigns request and SQL measurement callbacks around every request
    handler. It might arguably be part of the ``global_handlers`` initializer,
    but it's in a separate module so that it can be initialized separately,
    only in development mode.
    """

    app.before_request(_start_request_timing)
    app.after_request(_log_request_timing)

    sql_event.listens_for(Engine, "before_cursor_execute")(_start_db_timing)
    sql_event.listens_for(Engine, "after_cursor_execute")(_log_db_timing)

    return app


def _start_request_timing():
    g.start_time = time.monotonic_ns()


def _log_request_timing(response):
    if _is_static(request):
        return response

    duration_ns = time.monotonic_ns() - g.start_time
    duration_ms = round(duration_ns / 1_000_000, 2)

    sql_duration_ms = round(getattr(g, 'sql_time_ns', 0.0) / 1_000_000, 2)
    sql_query_count = getattr(g, 'sql_query_count', 0)

    logger = current_app.logger.getChild('timing')
    logger.info(f"[{duration_ms}ms] Full request total")
    logger.info(f"[{sql_duration_ms}ms] Full request SQL: {sql_query_count} queries")

    return response


# Reference:
# https://docs.sqlalchemy.org/en/20/faq/performance.html#how-can-i-profile-a-sqlalchemy-powered-application
#
def _start_db_timing(conn, cursor, statement, parameters, context, executemany):
    if 'sql_time_ns' not in g:
        g.sql_time_ns = 0.0
    if 'sql_query_count' not in g:
        g.sql_query_count = 0

    start_time = time.monotonic_ns()
    conn.info.setdefault("start_time", []).append(start_time)


def _log_db_timing(conn, cursor, statement, parameters, context, executemany):
    duration_ns = time.monotonic_ns() - conn.info["start_time"].pop(-1)
    duration_ms = round(duration_ns / 1_000_000, 2)

    g.sql_time_ns += duration_ns
    g.sql_query_count += 1

    if os.getenv('TIME'):
        logger = current_app.logger.getChild('timing')
        logger.info(f"[{duration_ms}ms] Query: {' '.join(statement.split('\n'))}")


def _is_static(request):
    return request.endpoint in ('static', 'admin.static', None)
