#!/usr/bin/env python3

import importlib.resources
import logging
import os

import dotenv
import passlib.context
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_config
import steins_feed_config.feeds
import steins_feed_logging
import steins_feed_model
import steins_feed_model.users

dotenv.load_dotenv()

config_logger = steins_feed_logging.LoggerFactory.get_logger(steins_feed_config.__name__)
steins_feed_logging.LoggerFactory.add_stream_handler(config_logger)
steins_feed_logging.LoggerFactory.set_level(config_logger, logging.INFO)

engine = steins_feed_model.EngineFactory.create_engine(database=os.environ["DB_NAME"])
pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")

user = steins_feed_model.users.User(
    name = os.environ["DEV_USER"],
    password = pwd_context.hash(os.environ["DEV_PASS"]),
    email = os.environ["DEV_MAIL"],
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
    with importlib.resources.open_text(steins_feed_config, "feeds.d/magazines.xml") as f:
        steins_feed_config.feeds.read_xml(
            session,
            f,
            user_name = os.environ["DEV_USER"],
            tag_name = "magazines",
        )

    with importlib.resources.open_text(steins_feed_config, "feeds.d/news.xml") as f:
        steins_feed_config.feeds.read_xml(
            session,
            f,
            user_name = os.environ["DEV_USER"],
            tag_name = "news",
        )

    with importlib.resources.open_text(steins_feed_config, "feeds.d/science.xml") as f:
        steins_feed_config.feeds.read_xml(
            session,
            f,
            user_name = os.environ["DEV_USER"],
            tag_name = "science",
        )

    with importlib.resources.open_text(steins_feed_config, "feeds.d/tech.xml") as f:
        steins_feed_config.feeds.read_xml(
            session,
            f,
            user_name = os.environ["DEV_USER"],
            tag_name = "tech",
        )
