import functools

import steins_feed_magic.util

def test_fold_left():
    assert steins_feed_magic.util.fold_left(
        "",
        range(5),
        lambda a, b: a + str(b),
    ) == "01234"

def test_apply_to():
    assert steins_feed_magic.util.apply_to(
        1,
        lambda x: 3 * x,
    ) == 3

def test_chain():
    func = steins_feed_magic.util.chain(
        lambda x: x + 1,
        lambda x: x + 2,
        lambda x: x + 3,
    )
    assert func(0) == 6

def test_concatenate():
    func = steins_feed_magic.util.concatenate(
        lambda x: x.split(","),
        lambda x: functools.reduce(lambda a, b: int(a) + int(b), x),
    )
    assert func("1,2,3") == 6

def test_map_over():
    func = steins_feed_magic.util.map_over(
        lambda x: 2 * x,
    )
    assert func(range(3)) == [0, 2, 4]
