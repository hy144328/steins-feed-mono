import typing

import fastapi
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_model

_ENGINE: typing.Optional[sqla.engine.Engine] = None

def set_up(
    username: typing.Optional[str],
    password: typing.Optional[str],
    host: typing.Optional[str],
    port: typing.Optional[str | int],
    database: typing.Optional[str],
):
    global _ENGINE

    _ENGINE = steins_feed_model.EngineFactory.create_engine(
        username = username,
        password = password,
        host = host,
        port = port,
        database = database,
    )

async def get_engine() -> sqla.engine.Engine:
    assert _ENGINE is not None
    return _ENGINE

Engine = typing.Annotated[sqla.engine.Engine, fastapi.Depends(get_engine)]

async def get_session(engine: Engine) -> typing.AsyncGenerator[sqla_orm.Session]:
    with sqla_orm.Session(engine) as session:
        yield session

Session = typing.Annotated[sqla_orm.Session, fastapi.Depends(get_session)]
