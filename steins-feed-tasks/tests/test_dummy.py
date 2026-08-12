import collections.abc

import celery
import celery.result
import pytest
import testcontainers.core.container
import testcontainers.core.image
import testcontainers.core.network
import testcontainers.redis

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
        "redis",
    ).with_exposed_ports(
        6379,
    ) as container:
        yield container

@pytest.fixture
def worker(
    network: testcontainers.core.network.Network,
    redis: testcontainers.redis.RedisContainer,
) -> collections.abc.Generator[testcontainers.core.container.DockerContainer]:
    with testcontainers.core.image.DockerImage("./") as image:
        with testcontainers.core.container.DockerContainer(str(image)).with_envs(
            BROKER_URL="redis://redis:6379/0",
            RESULT_BACKEND="redis://redis:6379/0",
        ).with_network(
            network,
        ).with_network_aliases(
            "worker",
        ) as container:
            yield container

def test_add(
    monkeypatch: pytest.MonkeyPatch,
    network: testcontainers.core.network.Network,
    redis: testcontainers.redis.RedisContainer,
    worker: testcontainers.core.container.DockerContainer,
):
    redis_host = redis.get_container_host_ip()
    redis_port = redis.get_exposed_port(6379)
    redis_url = f"redis://{redis_host}:{redis_port}/0"

    monkeypatch.setenv("BROKER_URL", redis_url)
    monkeypatch.setenv("RESULT_BACKEND", redis_url)

    import steins_feed_tasks.dummy

    assert isinstance(steins_feed_tasks.dummy.add, celery.Task)
    res = steins_feed_tasks.dummy.add.delay(x=3, y=7)
    assert isinstance(res, celery.result.AsyncResult)
    assert res.get() == 10
