import typing

import sqlalchemy as sqla

from . import feeds, items, users

class EngineFactory:
    @classmethod
    def create_engine(
        cls,
        drivername: str = "sqlite",
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        host: typing.Optional[str] = None,
        port: typing.Optional[typing.Union[int, str]] = None,
        database: typing.Optional[str] = None,
        echo: bool = False,
    ) -> sqla.engine.Engine:
        url = sqla.URL.create(
            drivername,
            username = username,
            password = password,
            host = host,
            port = int(port) if port is not None else None,
            database = database,
        )
        connect_args = {
            "check_same_thread": False,
            "timeout": 5,
        }
        return sqla.create_engine(
            url,
            connect_args = connect_args,
            echo = echo,
        )

    @classmethod
    def create_metadata(cls, engine: sqla.engine.Engine) -> sqla.MetaData:
        metadata = sqla.MetaData()
        metadata.reflect(bind=engine)
        return metadata

# SQLite check foreign keys.
@sqla.event.listens_for(sqla.engine.Engine, "connect")
def set_sqlite_pragma(dbapi_connection, connection_record):
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()
