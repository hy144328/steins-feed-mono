import functools
import typing

import numpy as np
import numpy.typing as npt
import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.pipeline

import steins_feed_model.feeds

from . import feature
from . import util

def build_classifier(
    lang: typing.Optional[steins_feed_model.feeds.Language] = None,
) -> sklearn.pipeline.Pipeline:
    extract_one = functools.partial(util.getattr_from, name="title")
    extract_many = util.map_over(extract_one)

    return sklearn.pipeline.make_pipeline(
        sklearn.pipeline.FunctionTransformer(extract_many),
        feature.CountVectorizer(lang),
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

    features = [
        *liked_items,
        *disliked_items,
    ]
    targets = [1 for _ in liked_items] + [-1 for _ in disliked_items]

    clf.fit(features, targets)

def predict_scores[T](
    clf: sklearn.pipeline.Pipeline,
    items: typing.Sequence[T],
) -> npt.NDArray[np.double]:
    res = clf.predict_proba(items)

    return functools.reduce(
        lambda a, b: a + b,
        [res[:, class_ct] * class_it for class_ct, class_it in enumerate(clf.classes_)],
    )
