import collections.abc

import celery
import celery.result
import pytest
import testcontainers.core.container
import testcontainers.core.image
import testcontainers.core.network
import testcontainers.redis
import yarl

REDIS_HOST = "redis"
REDIS_NAME = "0"
REDIS_PORT = 6379

@pytest.fixture
def network() -> collections.abc.Generator[testcontainers.core.network.Network]:
    with testcontainers.core.network.Network() as nw:
        yield nw

@pytest.fixture
def redis(
    network: testcontainers.core.network.Network,
) -> collections.abc.Generator[testcontainers.redis.RedisContainer]:
    with testcontainers.redis.RedisContainer().with_network(
        network,
    ).with_network_aliases(
        REDIS_HOST,
    ).with_exposed_ports(
        REDIS_PORT,
    ) as container:
        yield container

@pytest.fixture
def worker(
    network: testcontainers.core.network.Network,
) -> collections.abc.Generator[testcontainers.core.container.DockerContainer]:
    redis_url = yarl.URL.build(
        scheme="redis",
        host=REDIS_HOST,
        port=REDIS_PORT,
        path=f"/{REDIS_NAME}",
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

def test_add(
    monkeypatch: pytest.MonkeyPatch,
    redis: testcontainers.redis.RedisContainer,
    worker: testcontainers.core.container.DockerContainer,
):
    redis_url = yarl.URL.build(
        scheme="redis",
        host=redis.get_container_host_ip(),
        port=redis.get_exposed_port(REDIS_PORT),
        path=f"/{REDIS_NAME}",
    )

    monkeypatch.setenv("BROKER_URL", str(redis_url))
    monkeypatch.setenv("RESULT_BACKEND", str(redis_url))

    import steins_feed_tasks.dummy

    assert isinstance(steins_feed_tasks.dummy.add, celery.Task)
    res = steins_feed_tasks.dummy.add.delay(x=3, y=7)
    assert isinstance(res, celery.result.AsyncResult)
    assert res.get() == 10
