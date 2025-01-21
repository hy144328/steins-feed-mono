import typing

from .app import app

if typing.TYPE_CHECKING:
    import celery.result
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
def train_classifiers_all() -> "celery.result.GroupResult":
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
        job = celery.group(
            train_classifier.s(user_id=user_it.id, lang=lang_it)
            for user_it in session.execute(sqla.select(steins_feed_model.users.User)).scalars()
            for lang_it in steins_feed_model.feeds.Language
        )
        res = job()

    log.magic_logger.info("Finish train_classifiers_all.")
    return res

@app.task
def update_scores(
    user_id: int,
    item_ids: typing.Sequence[int],
) -> "celery.result.GroupResult":
    import itertools

    import celery

    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_model.items

    from . import db
    from . import log

    log.magic_logger.info(f"Start to update scores for {user_id}.")

    q = sqla.select(
        steins_feed_model.items.Item.id,
        steins_feed_model.feeds.Feed.language,
    ).join(
        steins_feed_model.items.Item.feed,
    ).join(
        steins_feed_model.items.Item.magic.and_(
            steins_feed_model.items.Magic.user_id == user_id,
        ),
        isouter = True,
    ).where(
        steins_feed_model.items.Item.id.in_(item_ids),
        steins_feed_model.items.Magic.item_id == None,
    ).order_by(
        steins_feed_model.feeds.Feed.language,
    )

    with sqla_orm.Session(db.engine) as session:
        items = itertools.groupby(
            session.execute(q).tuples(),
            key = lambda x: x[1],
        )

        assert isinstance(update_scores_by_language, celery.Task)
        signatures = []

        for lang_it, items_it in items:
            if lang_it is None:
                log.magic_logger.warning(f"Skip {len(list(items_it))} items without language.")
                continue

            sign_it = update_scores_by_language.s(
                user_id = user_id,
                item_ids = [item_it[0] for item_it in items_it],
                lang = lang_it,
            )
            signatures.append(sign_it)

    job = celery.group(*signatures)
    res = job()

    log.magic_logger.info(f"Finish to update scores for {user_id}.")
    return res

@app.task
def update_scores_by_language(
    user_id: int,
    item_ids: typing.Sequence[int],
    lang: "steins_feed_model.feeds.Language | str",
):
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_magic
    import steins_feed_magic.io
    import steins_feed_model.items

    from . import db
    from . import log

    log.magic_logger.info(f"Start to update scores for {user_id} and {lang}.")

    if not isinstance(lang, steins_feed_model.feeds.Language):
        lang = steins_feed_model.feeds.Language(lang)

    try:
        clf = steins_feed_magic.io.read_classifier(user_id, lang)
    except FileNotFoundError:
        log.magic_logger.warning(f"Skip {len(item_ids)} {lang} items without classifier.")
        return

    q = sqla.select(
        steins_feed_model.items.Item,
    ).where(
        steins_feed_model.items.Item.id.in_(item_ids),
    )

    with sqla_orm.Session(db.engine) as session:
        items = session.execute(q).scalars().all()
        scores = steins_feed_magic.predict_scores(clf, items)
        res = [
            {
                "user_id": user_id,
                "item_id": item_it.id,
                "score": score_it,
            }
            for item_it, score_it in zip(items, scores)
        ]

    stmt = sqla.insert(steins_feed_model.items.Magic)
    stmt = stmt.prefix_with("OR IGNORE", dialect="sqlite")

    with sqla_orm.Session(db.engine) as session:
        log.magic_logger.info(f"Update scores of {len(items)} {lang} items.")
        session.execute(stmt, res)
        session.commit()

    log.magic_logger.info(f"Finish to update scores for {user_id} and {lang}.")
