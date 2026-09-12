import collections.abc

import pytest
import testcontainers.core.network
import testcontainers.redis
import yarl

from . import shared

@pytest.fixture(scope="session")
def network() -> collections.abc.Generator[testcontainers.core.network.Network]:
    with testcontainers.core.network.Network() as nw:
        yield nw

@pytest.fixture(scope="session")
def redis(
    network: testcontainers.core.network.Network,
) -> collections.abc.Generator[testcontainers.redis.RedisContainer]:
    with testcontainers.redis.RedisContainer().with_network(
        network,
    ).with_network_aliases(
        shared.REDIS_HOST,
    ).with_exposed_ports(
        shared.REDIS_PORT,
    ) as container:
        try:
            yield container
        finally:
            out, err = container.get_logs()

            print("Redis stdout:")
            print(out.decode())

            print("Redis stderr:")
            print(err.decode())

@pytest.fixture
def app(
    monkeypatch: pytest.MonkeyPatch,
    redis: testcontainers.redis.RedisContainer,
):
    redis_url = yarl.URL.build(
        scheme="redis",
        host=redis.get_container_host_ip(),
        port=redis.get_exposed_port(shared.REDIS_PORT),
        path=f"/{shared.REDIS_NAME}",
    )

    monkeypatch.setenv("BROKER_URL", str(redis_url))
    monkeypatch.setenv("RESULT_BACKEND", str(redis_url))
