import steins_feed_magic.util

def test_fold_left():
    assert steins_feed_magic.util.fold_left(
        "",
        range(5),
        lambda a, b: a + str(b),
    ) == "01234"
