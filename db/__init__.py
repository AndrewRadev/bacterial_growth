import os
import tomllib
from pathlib import Path

import simplejson as json
import sqlalchemy as sql
import sqlalchemy.orm as orm
import flask_sqlalchemy

# Documentation on pooling: https://docs.sqlalchemy.org/en/20/core/pooling.html
APP_SQLALCHEMY_ENGINE_OPTIONS = {
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'json_serializer': lambda obj: json.dumps(obj, use_decimal=True),
    'json_deserializer': lambda obj: json.loads(obj, use_decimal=True),
}
"Custom configuration for SQLAlchemy"


def get_config(env: string=None) -> dict:
    "Returns the config in ``db/config.toml`` for the current environment"
    if env is None:
        env = os.getenv('APP_ENV', 'development')
    return tomllib.loads(Path('db/config.toml').read_text())[env]


def get_config_uri() -> str:
    "Returns the DB config as a single URI string"

    config = get_config()

    username = config.pop('username', '')
    password = config.pop('password', '')
    host     = config.pop('host', 'localhost')
    port     = config.pop('port', '3306')
    database = config.pop('database')

    return f"mysql+pymysql://{username}:{password}@{host}:{port}/{database}"


def get_cli_connection_params() -> list[str]:
    "Returns the DB config as a list of mysql client CLI parameters"

    config = get_config()

    if 'unix_socket' in config:
        extra_params = [f"--socket={config['unix_socket']}"]
    else:
        extra_params = ['--protocol=tcp']

    return [
        f'-h{config.get("host", "localhost")}',
        f'-u{config["username"]}',
        f'-p{config["password"]}',
        f'--port={config.get("port", "3306")}',
        *extra_params,
        config['database']
    ]


def get_connection():
    """
    Returns an SQLAlchemy Connection object.

    Usually, the code will use an SQLAlchemy Session, but this function is used
    for direct queries that do not need the ORM setup. For the most part, this
    is migrations.
    """

    return DB.connect()


def get_session(conn=None):
    """
    Returns an SQLAlchemy Session object.

    This may be used to wrap an existing connection into an ORM-aware session.
    If the given connection is actually a Session, it simply returns it.

    Part of the reason this is happening is because of legacy reasons, but it's
    also used to wrap a transaction connection from ``get_transaction``.
    Ideally, this shouldn't be necessary, but getting transactions to work for
    sessions has been a pain and this was the combination of entities that got
    us there. It may be simplified in the future.
    """

    if conn:
        if isinstance(conn, orm.Session):
            return conn
        elif isinstance(conn, sql.Connection):
            return orm.Session(bind=conn)
        else:
            message = f"The `conn` argument is of type {type(conn)}, it needs to be an SQLAlchemy connection"
            raise TypeError(message)
    else:
        return orm.Session(DB)


def get_transaction():
    "Returns a database connection that is initialized in transaction mode"
    return DB.begin()


def _create_engine():
    uri = get_config_uri()

    engine = sql.create_engine(
        uri,
        # Set echo=True for full query logging:
        **APP_SQLALCHEMY_ENGINE_OPTIONS,
        echo=False,
    )

    return engine


DB = _create_engine()
"An SQLAlchemy engine used to instantiate connections"

FLASK_DB = flask_sqlalchemy.SQLAlchemy()
"A Flask-SQLAlchemy object, needed for per-request connection handling"
