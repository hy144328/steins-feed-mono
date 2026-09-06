import collections.abc

import celery
import celery.result
import pytest
import testcontainers.core.container
import testcontainers.core.image
import testcontainers.core.network
import yarl

from . import shared

@pytest.fixture
def worker(
    network: testcontainers.core.network.Network,
) -> collections.abc.Generator[testcontainers.core.container.DockerContainer]:
    redis_url = yarl.URL.build(
        scheme="redis",
        host=shared.REDIS_HOST,
        port=shared.REDIS_PORT,
        path=f"/{shared.REDIS_NAME}",
    )

    with testcontainers.core.image.DockerImage(
        "../",
        dockerfile_path="steins-feed-tasks/Dockerfile",
    ) as image:
        with testcontainers.core.container.DockerContainer(str(image)).with_envs(
            BROKER_URL=str(redis_url),
            RESULT_BACKEND=str(redis_url),
        ).with_network(
            network,
        ) as container:
            yield container

def test_add(app, worker):
    import steins_feed_tasks.dummy

    assert isinstance(steins_feed_tasks.dummy.add, celery.Task)
    res = steins_feed_tasks.dummy.add.delay(x=3, y=7)
    assert isinstance(res, celery.result.AsyncResult)

    assert res.get(timeout=5) == 10
