import steins_feed_magic.classify
import steins_feed_model.feeds

def test_classify():
    clf = steins_feed_magic.classify.build_classifier(steins_feed_model.feeds.Language.ENGLISH)
    steins_feed_magic.classify.fit_classifier(clf, ["Donald Trump"], ["Joe Biden"])
    res = steins_feed_magic.classify.predict_scores(clf, ["Donald Duck", "Hunter Biden"])

    assert res[0] > 0
    assert res[1] < 0
