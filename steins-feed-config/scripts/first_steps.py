#!/usr/bin/env python3

import importlib.resources
import os

import dotenv
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_config
import steins_feed_config.feeds
import steins_feed_model
import steins_feed_model.users

dotenv.load_dotenv()

engine = steins_feed_model.EngineFactory.get_or_create_engine(database=os.environ["DB_NAME"])

user = steins_feed_model.users.User(
    name = "hansolo",
    password = "",
    email = "hans.yu@outlook.de",
)

q = sqla.insert(
    steins_feed_model.users.User,
).values(
    name = user.name,
    password = user.password,
    email = user.email,
)
q = q.prefix_with("OR IGNORE", dialect="sqlite")

with sqla_orm.Session(engine) as session:
    session.execute(q)
    session.commit()

with sqla_orm.Session(engine) as session:
    with importlib.resources.open_text(steins_feed_config, "feeds.d/news.xml") as f:
        steins_feed_config.feeds.read_xml(
            session,
            f,
            user_name = "hansolo",
            tag_name = "news",
        )
