import functools
import typing

import sklearn.feature_extraction.text
import sklearn.naive_bayes
import sklearn.pipeline

import numpy as np
import numpy.typing as npt
import steins_feed_model.feeds
import steins_feed_model.items

from . import feature

def build_classifier(
    lang: typing.Optional[steins_feed_model.feeds.Language] = None,
) -> sklearn.pipeline.Pipeline:
    def extract_texts(items: typing.Sequence[steins_feed_model.items.Item]) -> list[str]:
        return [item_it.title for item_it in items]

    return sklearn.pipeline.make_pipeline(
        sklearn.pipeline.FunctionTransformer(extract_texts),
        feature.CountVectorizer(lang),
        sklearn.feature_extraction.text.TfidfTransformer(),
        sklearn.naive_bayes.MultinomialNB(fit_prior=False),
    )

def fit_pipeline(
    clf: sklearn.pipeline.Pipeline,
    liked_items: typing.Sequence[steins_feed_model.items.Item],
    disliked_items: typing.Sequence[steins_feed_model.items.Item],
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

def predict_scores(
    clf: sklearn.pipeline.Pipeline,
    items: typing.Sequence[steins_feed_model.items.Item],
) -> npt.NDArray[np.double]:
    res = clf.predict_proba(items)

    return functools.reduce(
        lambda a, b: a + b,
        [res[:, class_ct] * class_it for class_ct, class_it in enumerate(clf.classes_)],
    )
