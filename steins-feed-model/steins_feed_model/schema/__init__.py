import sqlalchemy as sqla

from . import feeds, items, users

def create_schema(conn: sqla.Connection):
    users.create_schema(conn)
    feeds.create_schema(conn)
    items.create_schema(conn)
