import typing

import sqlalchemy as sqla

class EngineFactory:
    _obj: typing.Optional[sqla.engine.Engine]

    @classmethod
    def get_or_create_engine(
        cls,
        drivername: str = "sqlite",
        username: typing.Optional[str] = None,
        password: typing.Optional[str] = None,
        host: typing.Optional[str] = None,
        port: typing.Optional[int] = None,
        database: typing.Optional[str] = None,
    ) -> sqla.engine.Engine:
        if cls._obj is None:
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

            cls._obj = sqla.create_engine(url, connect_args = connect_args)

        return cls._obj

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
