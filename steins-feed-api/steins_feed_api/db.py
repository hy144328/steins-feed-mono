import typing

import sqlalchemy as sqla

import steins_feed_model

engine: typing.Optional[sqla.engine.Engine] = None

def set_up(
    username: typing.Optional[str],
    password: typing.Optional[str],
    host: typing.Optional[str],
    port: typing.Optional[str | int],
    database: typing.Optional[str],
):
    global engine

    engine = steins_feed_model.EngineFactory.create_engine(
        username = username,
        password = password,
        host = host,
        port = port,
        database = database,
    )
