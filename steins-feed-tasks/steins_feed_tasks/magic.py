import logging
import os
import typing

import steins_feed_logging

from .app import app

if typing.TYPE_CHECKING:
    import steins_feed_model.feeds

try:
    os.mkdir("logs.d")
except FileExistsError:
    pass

with open("logs.d/steins_feed_magic.log", "a") as f:
    magic_logger = steins_feed_logging.LoggerFactory.get_logger("steins_feed_magic")
    steins_feed_logging.LoggerFactory.add_file_handler(magic_logger, f)
    steins_feed_logging.LoggerFactory.set_level(magic_logger, level=logging.INFO)

@app.task
def train_classifier(
    user_id: int,
    lang: "steins_feed_model.feeds.Language | str",
):
    import sqlalchemy.orm as sqla_orm

    import steins_feed_magic
    import steins_feed_magic.db
    import steins_feed_magic.io
    import steins_feed_model.feeds

    from .db import engine

    if not isinstance(lang, steins_feed_model.feeds.Language):
        lang = steins_feed_model.feeds.Language(lang)

    clf = steins_feed_magic.build_classifier(lang)

    with sqla_orm.Session(engine) as session:
        liked_items = steins_feed_magic.db.liked_items(session, user_id, lang)
        disliked_items = steins_feed_magic.db.disliked_items(session, user_id, lang)

        try:
            steins_feed_magic.fit_classifier(
                clf,
                liked_items = liked_items,
                disliked_items = disliked_items,
            )
            steins_feed_magic.io.write_classifier(clf, 1, lang, force=True)
        except ValueError as e:
            magic_logger.warning(e)

@app.task
def train_classifiers_all():
    import celery
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_model.feeds
    import steins_feed_model.users

    from .db import engine

    res = []

    with sqla_orm.Session(engine) as session:
        for user_it in session.execute(sqla.select(steins_feed_model.users.User)).scalars():
            for lang_it in steins_feed_model.feeds.Language:
                assert isinstance(train_classifier, celery.Task)
                task_it = train_classifier.delay(user_it.id, lang_it)
                res.append((user_it.id, lang_it, task_it.id))

    return res
