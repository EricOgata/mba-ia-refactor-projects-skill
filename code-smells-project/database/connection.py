"""Camada de persistência — conexão SQLite com escopo de request.

Resolve QUAL-04 (estado global mutável): não há mais conexão singleton
compartilhada entre requests. Cada request recebe sua própria conexão,
fechada no teardown pelo Flask.
"""

import sqlite3

from flask import g

from config import Config
from database import schema


def _connect():
    conn = sqlite3.connect(Config.DATABASE_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def get_db():
    """Devolve a conexão do request atual, criando-a se necessário."""
    if "db" not in g:
        g.db = _connect()
        schema.ensure_schema(g.db)
    return g.db


def close_db(exc=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_app(app):
    app.teardown_appcontext(close_db)
