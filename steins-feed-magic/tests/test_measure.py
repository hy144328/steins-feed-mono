import steins_feed_magic.measure

def test_entropy_bernoulli():
    assert steins_feed_magic.measure.entropy_bernoulli(0) == 0
    assert steins_feed_magic.measure.entropy_bernoulli(0.5) == 1
    assert steins_feed_magic.measure.entropy_bernoulli(1) == 0
