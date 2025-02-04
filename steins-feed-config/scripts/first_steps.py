#!/usr/bin/env python3

import logging.config
import os
import tomllib

import dotenv
import passlib.context
import sqlalchemy as sqla
import sqlalchemy.exc as sqla_exc
import sqlalchemy.orm as sqla_orm

import steins_feed_config
import steins_feed_model
import steins_feed_model.users

dotenv.load_dotenv()

logger = logging.getLogger()

with open(os.path.join(os.path.dirname(__file__), "first_steps_logging.toml"), "rb") as f:
    logging.config.dictConfig(tomllib.load(f))

engine = steins_feed_model.EngineFactory.create_engine(database=os.environ["DB_NAME"])
pwd_context = passlib.context.CryptContext(schemes=["bcrypt"], deprecated="auto")

with sqla_orm.Session(engine) as session:
    try:
        user = steins_feed_model.users.User(
            name = os.environ["DEV_USER"],
            password = pwd_context.hash(os.environ["DEV_PASS"]),
            email = os.environ["DEV_MAIL"],
        )
        session.add(user)
        session.commit()
    except sqla_exc.IntegrityError:
        logger.warning(f"User {os.environ["DEV_USER"]} already exists.")
        session.rollback()

        q = sqla.select(
            steins_feed_model.users.User,
        ).where(
            steins_feed_model.users.User.name == os.environ["DEV_USER"],
        )
        user = session.execute(q).scalars().one()

    with open("feeds.xml", "r") as f:
        steins_feed_config.read_xml(
            session,
            f,
            user_id = user.id,
        )
