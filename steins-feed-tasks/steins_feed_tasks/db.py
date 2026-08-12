import os

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

url = sqla.URL.create(
    "sqlite",
    username = os.getenv("DB_USER"),
    password = os.getenv("DB_PASS"),
    host = os.getenv("DB_HOST"),
    port = int(os.environ["DB_PORT"]) if "DB_PORT" in os.environ else None,
    database = os.getenv("DB_NAME"),
)
engine = sqla.create_engine(url)
Session = sqla_orm.sessionmaker(engine)
