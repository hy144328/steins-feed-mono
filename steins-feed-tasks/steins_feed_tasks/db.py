import os

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_model.base

url = sqla.URL.create(
    "sqlite",
    username = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS"),
    host = os.getenv("DB_HOST"),
    port = int(os.environ["DB_PORT"]) if "DB_PORT" in os.environ else None,
    database = os.getenv("DB_NAME"),
)
engine = sqla.create_engine(url)
steins_feed_model.base.Base.metadata.create_all(engine)

Session = sqla_orm.sessionmaker(engine)
