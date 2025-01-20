import typing

import celery
import celery.result

from .app import app

if typing.TYPE_CHECKING:
    import steins_feed_model.feeds

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

    from . import db
    from . import log

    log.magic_logger.info(f"Start train_classifier: {user_id}, {lang}.")

    if not isinstance(lang, steins_feed_model.feeds.Language):
        lang = steins_feed_model.feeds.Language(lang)

    clf = steins_feed_magic.build_classifier(lang)

    with sqla_orm.Session(db.engine) as session:
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
            log.magic_logger.warning(e)

    log.magic_logger.info(f"Finish train_classifier: {user_id}, {lang}.")

@app.task
def train_classifiers_all() -> celery.result.GroupResult:
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_model.feeds
    import steins_feed_model.users

    from . import db
    from . import log

    log.magic_logger.info("Start train_classifiers_all.")

    assert isinstance(train_classifier, celery.Task)

    with sqla_orm.Session(db.engine) as session:
        job = celery.group(
            train_classifier.s(user_it.id, lang_it)
            for user_it in session.execute(sqla.select(steins_feed_model.users.User)).scalars()
            for lang_it in steins_feed_model.feeds.Language
        )
        res = job()

    log.magic_logger.info("Finish train_classifiers_all.")
    assert isinstance(res, celery.result.GroupResult)
    return res

@app.task
def update_scores(
    user_id: int,
    item_ids: typing.Sequence[int],
):
    import itertools

    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_magic
    import steins_feed_magic.io
    import steins_feed_model.items

    from . import db
    from . import log

    log.magic_logger.info(f"Start update_scores for {user_id}.")

    with sqla_orm.Session(db.engine) as session:
        all_items = (
            session.get_one(
                steins_feed_model.items.Item,
                item_id,
                options = [
                    sqla_orm.joinedload(steins_feed_model.items.Item.feed),
                    sqla_orm.joinedload(
                        steins_feed_model.items.Item.magic.and_(
                            steins_feed_model.items.Magic.user_id == user_id,
                        ),
                    ),
                ],
            )
            for item_id in item_ids
        )
        unscored_items = (
            item_it
            for item_it in all_items
            if item_it.feed.language is not None and len(item_it.magic) > 0
        )
        grouped_items = itertools.groupby(unscored_items, key=lambda x: x.feed.language)

        q = sqla.insert(steins_feed_model.items.Magic)
        q = q.prefix_with("OR IGNORE", dialect="sqlite")

        for k, vs in grouped_items:
            vs = list(vs)

            if k is None:
                log.magic_logger.warning(f"Skip {len(vs)} items without language.")
                continue

            try:
                clf = steins_feed_magic.io.read_classifier(user_id, k)
            except FileNotFoundError:
                log.magic_logger.warning(f"Skip {len(vs)} {k} items without classifier.")
                continue

            scores = steins_feed_magic.predict_scores(clf, vs)
            res = [
                {
                    "user_id": user_id,
                    "item_id": item_it.id,
                    "score": score_it,
                }
                for item_it, score_it in zip(vs, scores)
            ]

            log.magic_logger.info(f"Update scores of {len(vs)} {k} items.")
            session.execute(q, res)

        session.commit()

    log.magic_logger.info(f"Finish update_scores for {user_id}.")
