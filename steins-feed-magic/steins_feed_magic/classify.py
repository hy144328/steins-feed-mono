import functools
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
    except KeyError:
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
    if len(liked_items) == 0:
        raise ValueError("No likes.")

    if len(disliked_items) == 0:
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

    return functools.reduce(
        lambda a, b: a + b,
        [res[:, class_ct] * class_it.value for class_ct, class_it in enumerate(clf.classes_)],
    )
