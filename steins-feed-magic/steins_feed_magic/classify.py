import logging
import typing

import numpy as np
import numpy.typing as npt
import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.pipeline

import steins_feed_model.feeds
import steins_feed_model.items

from . import stem

logger = logging.getLogger(__name__)

def build_classifier(
    lang: steins_feed_model.feeds.Language,
) -> sklearn.pipeline.Pipeline:
    try:
        vect = stem.StemmingCountVectorizer(lang)
    except KeyError:    # pragma: no cover
        logger.warning(f"No stemmer of language {lang}.")
        vect = sklearn.feature_extraction.text.CountVectorizer()

    return sklearn.pipeline.make_pipeline(
        vect,
        sklearn.feature_extraction.text.TfidfTransformer(),
        sklearn.naive_bayes.MultinomialNB(fit_prior=False),
    )

def fit_classifier[T](
    clf: sklearn.pipeline.Pipeline,
    liked_items: typing.Sequence[T],
    disliked_items: typing.Sequence[T],
):
    if len(liked_items) == 0:   # pragma: no cover
        raise ValueError("No likes.")

    if len(disliked_items) == 0:    # pragma: no cover
        raise ValueError("No dislikes.")

    features = [*liked_items, *disliked_items]
    targets = [
        steins_feed_model.items.LikeStatus.UP
        for _ in liked_items
    ] + [
        steins_feed_model.items.LikeStatus.DOWN
        for _ in disliked_items
    ]

    clf.fit(features, targets)

def predict_scores[T](
    clf: sklearn.pipeline.Pipeline,
    items: typing.Sequence[T],
) -> npt.NDArray[np.double]:
    res = clf.predict_proba(items)
    classes = clf.classes_.tolist()

    idx_liked = classes.index(steins_feed_model.items.LikeStatus.UP.value)
    res_liked = res[:, idx_liked]

    idx_disliked = classes.index(steins_feed_model.items.LikeStatus.DOWN.value)
    res_disliked = res[:, idx_disliked]

    return res_liked - res_disliked
