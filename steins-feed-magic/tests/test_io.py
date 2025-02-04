import tempfile

import sklearn.pipeline

import steins_feed_magic.io
import steins_feed_model.feeds

def test_write_and_read_classifier():
    with tempfile.TemporaryDirectory() as temp_dir:
        steins_feed_magic.io.write_classifier(
            sklearn.pipeline.Pipeline(steps=[]),
            temp_dir,
            user_id = 0,
            lang = steins_feed_model.feeds.Language.ENGLISH,
            force = True,
        )
        clf = steins_feed_magic.io.read_classifier(
            temp_dir,
            user_id = 0,
            lang = steins_feed_model.feeds.Language.ENGLISH,
        )
        assert clf.steps == []
