import steins_feed_model.feeds
import steins_feed_magic.stem

def test_english():
    vect = steins_feed_magic.stem.StemmingCountVectorizer(steins_feed_model.feeds.Language.ENGLISH)
    tokenize = vect.build_tokenizer()
    assert tokenize("gives giving bottles") == ["give", "give", "bottl"]
