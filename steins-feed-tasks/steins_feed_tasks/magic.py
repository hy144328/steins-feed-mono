import logging
import typing

from .app import app

logger = logging.getLogger(__name__)

if typing.TYPE_CHECKING:
    import steins_feed_model.feeds

@app.task
def train_classifier(
    user_id: int,
    lang: "steins_feed_model.feeds.Language | str",
):
    import os

    import sqlalchemy.orm as sqla_orm

    import steins_feed_magic.classify
    import steins_feed_magic.db
    import steins_feed_magic.io
    import steins_feed_magic.parse
    import steins_feed_model.feeds

    from . import db

    logger.info(f"Start train_classifier: {user_id}, {lang}.")

    if not isinstance(lang, steins_feed_model.feeds.Language):
        lang = steins_feed_model.feeds.Language(lang)

    clf = steins_feed_magic.classify.build_classifier(lang)

    with sqla_orm.Session(db.engine) as session:
        liked_items = [
            steins_feed_magic.parse.text_content(item_it.title)
            for item_it in steins_feed_magic.db.liked_items(session, user_id, lang)
        ]
        disliked_items = [
            steins_feed_magic.parse.text_content(item_it.title)
            for item_it in steins_feed_magic.db.disliked_items(session, user_id, lang)
        ]

        try:
            steins_feed_magic.classify.fit_classifier(
                clf,
                liked_items = liked_items,
                disliked_items = disliked_items,
            )
            steins_feed_magic.io.write_classifier(
                clf,
                os.environ["MAGIC_FOLDER"],
                user_id = user_id,
                lang = lang,
                force = True,
            )
            steins_feed_magic.db.reset_magic(
                session,
                user_id = user_id,
                lang = lang,
            )
        except ValueError as e:
            logger.warning(e)

    logger.info(f"Finish train_classifier: {user_id}, {lang}.")

@app.task
def train_classifiers_all():
    import celery
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_model.feeds
    import steins_feed_model.users

    from . import db

    logger.info("Start train_classifiers_all.")

    assert isinstance(train_classifier, celery.Task)

    with sqla_orm.Session(db.engine) as session:
        q_users = sqla.select(steins_feed_model.users.User)
        job = celery.group(
            train_classifier.s(user_id=user_it.id, lang=lang_it)
            for user_it in session.execute(q_users).scalars()
            for lang_it in steins_feed_model.feeds.Language
        )
        job()

    logger.info("Finish train_classifiers_all.")

@app.task
def calculate_scores(
    item_ids: typing.Sequence[int],
    user_id: int,
    lang: "steins_feed_model.feeds.Language | str",
) -> list[typing.Tuple[int, float]] | list[typing.Tuple[int, None]]:
    import os

    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_magic.classify
    import steins_feed_magic.io
    import steins_feed_magic.parse
    import steins_feed_model.items

    from . import db

    logger.info(f"Start to calculate scores for {user_id} and {lang}.")

    if not isinstance(lang, steins_feed_model.feeds.Language):
        lang = steins_feed_model.feeds.Language(lang)

    try:
        clf = steins_feed_magic.io.read_classifier(
            os.environ["MAGIC_FOLDER"],
            user_id = user_id,
            lang = lang,
        )
    except FileNotFoundError:
        logger.warning(f"Skip {len(item_ids)} {lang} items without classifier.")
        return [(item_id, None) for item_id in item_ids]

    q = sqla.select(
        steins_feed_model.items.Item,
    ).where(
        steins_feed_model.items.Item.id.in_(item_ids),
    )
    logger.info(f"Calculate scores of {len(item_ids)} {lang} items.")

    with sqla_orm.Session(db.engine) as session:
        items = session.execute(q).scalars().all()
        scores = steins_feed_magic.classify.predict_scores(
            clf,
            [
                steins_feed_magic.parse.text_content(item_it.title)
                for item_it in items
            ],
        )
        res = [
            (item_it.id, score_it)
            for item_it, score_it in zip(items, scores)
        ]

    logger.info(f"Finish to calculate scores for {user_id} and {lang}.")
    return res

@app.task
def update_scores(
    item_scores: typing.Sequence[typing.Tuple[int, typing.Optional[float]]],
    user_id: int,
):
    import sqlalchemy as sqla
    import sqlalchemy.orm as sqla_orm

    import steins_feed_model.items

    from . import db

    logger.info(f"Start to update scores for {user_id}.")

    q = sqla.insert(steins_feed_model.items.Magic)
    q = q.prefix_with("OR IGNORE", dialect="sqlite")

    res = [
        {
            "user_id": user_id,
            "item_id": item_id,
            "score": score_it,
        }
        for item_id, score_it in item_scores
        if score_it is not None
    ]

    with sqla_orm.Session(db.engine) as session:
        logger.info(f"Update scores of {len(item_scores)} items.")
        session.execute(q, res)
        session.commit()

    logger.info(f"Finish to update scores for {user_id}.")

@app.task
def analyze_text(
    s: str,
    user_id: int,
    lang: "steins_feed_model.feeds.Language| str",
) -> dict[str, float]:
    import os

    import steins_feed_magic.classify
    import steins_feed_magic.io
    import steins_feed_magic.parse
    import steins_feed_model.feeds

    logger.info(f"Start to analyze text for {user_id} and {lang}.")

    if not isinstance(lang, steins_feed_model.feeds.Language):
        lang = steins_feed_model.feeds.Language(lang)

    try:
        clf = steins_feed_magic.io.read_classifier(os.environ["MAGIC_FOLDER"], user_id, lang)
        text_vectorizer = clf.steps[0][1]
        text_tokenizer = text_vectorizer.build_tokenizer(skip_stem=True)
    except FileNotFoundError:
        logger.warning(f"Skip text without classifier.")
        return {}

    words = text_tokenizer(steins_feed_magic.parse.text_content(s))
    res = dict(zip(words, steins_feed_magic.classify.predict_scores(clf, words)))

    logger.info(f"Finish to analyze text with {len(words)} words for {user_id} and {lang}.")
    return res
