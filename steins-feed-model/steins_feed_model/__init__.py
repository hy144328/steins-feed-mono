import sqlalchemy as sqla

from . import feeds, items, users

# SQLite check foreign keys.
@sqla.event.listens_for(sqla.engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
