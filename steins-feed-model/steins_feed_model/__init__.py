import typing

import sqlalchemy as sqla

from . import feeds, items, users

class EngineFactory:
    _engine: typing.Optional[sqla.engine.Engine] = None

    @classmethod
    def get_or_create_engine(
        cls,
        drivername: str = "sqlite",
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        host: typing.Optional[str] = None,
        port: typing.Optional[int] = None,
        database: typing.Optional[str] = None,
        echo: bool = False,
    ) -> sqla.engine.Engine:
        if cls._engine is None:
            url = sqla.URL.create(
                drivername,
                username = username,
                password = password,
                host = host,
                port = port,
                database = database,
            )
            connect_args = {
                "check_same_thread": False,
                "timeout": 5,
            }

            cls._engine = sqla.create_engine(
                url,
                connect_args = connect_args,
                echo = echo,
            )

        return cls._engine

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
