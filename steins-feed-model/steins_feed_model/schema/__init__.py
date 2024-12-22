import sqlalchemy as sqla

from . import feeds, items, users

def create_schema(
    conn: sqla.Connection,
    meta: sqla.MetaData,
):
    users.create_schema(conn, meta)
    feeds.create_schema(conn, meta)
    items.create_schema(conn, meta)
