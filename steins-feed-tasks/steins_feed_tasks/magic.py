import typing

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
            steins_feed_magic.db.reset_magic(session, user_id, lang)
        except ValueError as e:
            log.magic_logger.warning(e)

    log.magic_logger.info(f"Finish train_classifier: {user_id}, {lang}.")

@app.task
def train_classifiers_all():
    import celery
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_model.feeds
    import steins_feed_model.users

    from . import db
    from . import log

    log.magic_logger.info("Start train_classifiers_all.")

    assert isinstance(train_classifier, celery.Task)

    with sqla_orm.Session(db.engine) as session:
        q_users = sqla.select(steins_feed_model.users.User)
        job = celery.group(
            train_classifier.s(user_id=user_it.id, lang=lang_it)
            for user_it in session.execute(q_users).scalars()
            for lang_it in steins_feed_model.feeds.Language
        )
        job()

    log.magic_logger.info("Finish train_classifiers_all.")

@app.task
def calculate_scores(
    item_ids: typing.Sequence[int],
    user_id: int,
    lang: "steins_feed_model.feeds.Language | str",
) -> list[typing.Tuple[int, float]] | list[typing.Tuple[int, None]]:
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_magic
    import steins_feed_magic.io
    import steins_feed_model.items

    from . import db
    from . import log

    log.magic_logger.info(f"Start to calculate scores for {user_id} and {lang}.")

    if not isinstance(lang, steins_feed_model.feeds.Language):
        lang = steins_feed_model.feeds.Language(lang)

    try:
        clf = steins_feed_magic.io.read_classifier(user_id, lang)
    except FileNotFoundError:
        log.magic_logger.warning(f"Skip {len(item_ids)} {lang} items without classifier.")
        return [(item_id, None) for item_id in item_ids]

    q = sqla.select(
        steins_feed_model.items.Item,
    ).where(
        steins_feed_model.items.Item.id.in_(item_ids),
    )
    log.magic_logger.info(f"Calculate scores of {len(item_ids)} {lang} items.")

    with sqla_orm.Session(db.engine) as session:
        items = session.execute(q).scalars().all()
        scores = steins_feed_magic.predict_scores(clf, items)
        res = [
            (item_it.id, score_it)
            for item_it, score_it in zip(items, scores)
        ]

    log.magic_logger.info(f"Finish to calculate scores for {user_id} and {lang}.")
    return res

@app.task
def update_scores(
    item_scores: typing.Sequence[typing.Tuple[int, float]],
    user_id: int,
    lang: "steins_feed_model.feeds.Language | str",
):
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_model.items

    from . import db
    from . import log

    log.magic_logger.info(f"Start to update scores for {user_id} and {lang}.")

    q = sqla.insert(steins_feed_model.items.Magic)
    q = q.prefix_with("OR IGNORE", dialect="sqlite")

    res = [
        {
            "user_id": user_id,
            "item_id": item_id,
            "score": score_it,
        }
        for item_id, score_it in item_scores
    ]

    with sqla_orm.Session(db.engine) as session:
        log.magic_logger.info(f"Update scores of {len(item_scores)} {lang} items.")
        session.execute(q, res)
        session.commit()

    log.magic_logger.info(f"Finish to update scores for {user_id} and {lang}.")
