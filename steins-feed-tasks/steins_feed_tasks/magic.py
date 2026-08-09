import collections.abc
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

    with db.Session(expire_on_commit=False) as session:
        with session.begin():
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

            with session.begin():
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

    import steins_feed_model.feeds
    import steins_feed_model.users

    from . import db

    logger.info("Start train_classifiers_all.")

    assert isinstance(train_classifier, celery.Task)

    with db.Session() as session:
        q_users = sqla.select(steins_feed_model.users.User)
        job = celery.group(
            train_classifier.s(user_id=user_it.id, lang=lang_it)
            for user_it in session.scalars(q_users)
            for lang_it in steins_feed_model.feeds.Language
        )
        job()

    logger.info("Finish train_classifiers_all.")

@app.task
def calculate_scores(
    item_ids: collections.abc.Sequence[int],
    user_id: int,
    lang: "steins_feed_model.feeds.Language | str",
) -> list[tuple[int, float]] | list[tuple[int, None]]:
    import os

    import sqlalchemy as sqla

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

    with db.Session(expire_on_commit=False) as session:
        items = session.scalars(q).all()

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
    item_scores: collections.abc.Sequence[tuple[int, float | None]],
    user_id: int,
):
    import sqlalchemy as sqla

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

    logger.info(f"Update scores of {len(item_scores)} items.")
    with db.Session.begin() as session:
        session.execute(q, res)

    logger.info(f"Finish to update scores for {user_id}.")

@app.task
def analyze_text(
    s: str,
    user_id: int,
    lang: "steins_feed_model.feeds.Language| str",
) -> list[tuple[str, str, float]]:
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
        text_preprocessor = text_vectorizer.build_preprocessor()
        text_tokenizer = text_vectorizer.build_tokenizer()
        text_tokenizer_wo_stem = text_vectorizer.build_tokenizer(skip_stem=True)
    except FileNotFoundError:
        logger.warning(f"Skip text without classifier.")
        return []

    content = steins_feed_magic.parse.text_content(s)
    words = text_tokenizer_wo_stem(content)
    words_stem = text_tokenizer(text_preprocessor(content))
    scores = steins_feed_magic.classify.predict_scores(clf, words)
    res = zip(words, words_stem, scores)

    logger.info(f"Finish to analyze text with {len(words)} words for {user_id} and {lang}.")
    return list(res)
