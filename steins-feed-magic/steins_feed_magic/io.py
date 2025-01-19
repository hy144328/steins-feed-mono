import contextlib
import os
import pickle
import typing

import sklearn.pipeline

import steins_feed_model.feeds

def mkdir_p(*nested_folders: str):
    for depth_it in range(len(nested_folders)):
        try:
            os.mkdir(os.path.join(*nested_folders[:depth_it + 1]))
        except FileExistsError:
            pass

@contextlib.contextmanager
def open_pickle(
    user_id: int,
    lang: steins_feed_model.feeds.Language,
    open_mode: str = "r",
    force: bool = False,
) -> typing.Generator[typing.IO]:
    if force:
        mkdir_p(os.environ["MAGIC_FOLDER"], str(user_id))

    folder_name = os.path.join(os.environ["MAGIC_FOLDER"], str(user_id))
    file_name = f"{lang}.pickle"

    with open(os.path.join(folder_name, file_name), f"{open_mode}b") as f:
        yield f

def read_classifier(
    user_id: int,
    lang: steins_feed_model.feeds.Language,
) -> sklearn.pipeline.Pipeline:
    with open_pickle(user_id, lang, "r") as f:
        return pickle.load(f)

def write_classifier(
    clf: sklearn.pipeline.Pipeline,
    user_id: int,
    lang: steins_feed_model.feeds.Language,
    force: bool = False,
):
    with open_pickle(user_id, lang, open_mode="w", force=force) as f:
        pickle.dump(clf, f)
