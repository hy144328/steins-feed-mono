#!/usr/bin/env python3

import os

import celery
import celery.result
import dotenv
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

dotenv.load_dotenv()

import steins_feed_model
import steins_feed_tasks.magic

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

assert isinstance(steins_feed_tasks.magic.train_classifier, celery.Task)

with Session() as session:
    tasks = [
        steins_feed_tasks.magic.train_classifier.s(
            user_id=user_it.id,
            lang=lang_it,
        )
        for user_it in session.scalars(sqla.select(steins_feed_model.users.User))
        for lang_it in steins_feed_model.feeds.Language
    ]
    job = celery.group(tasks)
    res = job()

assert isinstance(res, celery.result.GroupResult)
res.join_native(timeout=60)
