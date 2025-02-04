import itertools
import random

import pytest

import steins_feed_magic.sample

@pytest.mark.parametrize(
    "n,k,no_samples",
    [
        (100, 10, 100),
        (100, 10, 1000),
        (100, 10, 10000),
    ],
)
def test_uniform(n: int, k: int, no_samples: int):
    rng = random.Random(0)
    res = dict(zip(range(n), itertools.repeat(0, n)))

    for _ in range(no_samples):
        reservoir = steins_feed_magic.sample.Reservoir(rng, k)

        for i in range(n):
            reservoir.add(i)

        for i in reservoir.sample:
            res[i] += 1

    avg = no_samples * k // n
    var = sum((res[i] - avg) * (res[i] - avg) for i in range(n)) / n
    assert var / no_samples < 0.1
