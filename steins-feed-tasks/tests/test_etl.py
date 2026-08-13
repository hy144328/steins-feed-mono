import collections.abc
import os.path
import tempfile
import typing

import celery
import celery.result
import pytest
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import testcontainers.core.container
import testcontainers.core.image
import testcontainers.core.network
import testcontainers.redis
import wiremock.testing.testcontainer
import yarl

import steins_feed_config
import steins_feed_model.base
import steins_feed_model.items

DB_NAME = "steins.db"
REDIS_HOST = "redis"
REDIS_NAME = "0"
REDIS_PORT = 6379
RSS_HOST = "rss"
RSS_PATH = "/rss.xml"
RSS_PORT = 8080
VOLUME_PATH = "/usr/src/app/data"

@pytest.fixture
def volume() -> collections.abc.Generator[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def database(volume: str) -> str:
    return os.path.join(volume, DB_NAME)

@pytest.fixture
def engine(database: str) -> sqla.Engine:
    engine = sqla.create_engine(sqla.URL.create("sqlite", database=database))
    steins_feed_model.base.Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def Session(engine: sqla.Engine) -> sqla_orm.sessionmaker[sqla_orm.Session]:
    return sqla_orm.sessionmaker(engine)

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
    volume: str,
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
            DB_NAME=os.path.join(VOLUME_PATH, DB_NAME),
            RESULT_BACKEND=str(redis_url),
        ).with_network(
            network,
        ).with_volume_mapping(
            volume,
            VOLUME_PATH,
            mode="rw",
        ) as container:
            yield container

@pytest.fixture
def server(
    network: testcontainers.core.network.Network,
) -> collections.abc.Generator[testcontainers.core.container.DockerContainer]:
    with wiremock.testing.testcontainer.WireMockContainer(secure=False).with_mapping(
        "rss.json",
        {
            "request": {
                "method": "GET",
                "url": str(yarl.URL.build(path=RSS_PATH)),
            },
            "response": {
                "status": 200,
                "headers": {
                    "Content-Type": "application/rss+xml",
                },
                "body": """
<?xml version="1.0" encoding="utf-8"?>
<rss xmlns:media="http://search.yahoo.com/mrss/" xmlns:dc="http://purl.org/dc/elements/1.1/" version="2.0">
  <channel>
    <title>The Guardian</title>
    <link>https://www.theguardian.com/uk</link>
    <pubDate>Wed, 12 Aug 2026 20:51:33 GMT</pubDate>
    <item>
      <title>How the Other Half Loves review</title>
      <link>https://www.theguardian.com/stage/2026/aug/12/how-the-other-half-loves-review-old-vic-london-alan-ayckbourn-roger-allam</link>
      <description>The Old Vic, London</description>
      <pubDate>Wed, 12 Aug 2026 17:00:34 GMT</pubDate>
    </item>
  </channel>
</rss>
                """,
            },
        },
    ).with_network(
        network,
    ).with_network_aliases(
        RSS_HOST,
    ) as container:
        yield container

@pytest.fixture
def config_file() -> collections.abc.Generator[typing.TextIO]:
    rss_url = yarl.URL.build(
        scheme="http",
        host=RSS_HOST,
        port=RSS_PORT,
        path=RSS_PATH,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
            f.write(f"""
<root>
  <feed>
    <title>The Guardian</title>
    <link>{rss_url}</link>
    <lang>English</lang>
  </feed>
</root>
            """)

        with open(f.name, "r") as f:
            yield f

def test_parse_feeds(
    monkeypatch: pytest.MonkeyPatch,
    redis: testcontainers.redis.RedisContainer,
    worker: testcontainers.core.container.DockerContainer,
    server: wiremock.testing.testcontainer.WireMockContainer,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    config_file: typing.TextIO,
):
    redis_url = yarl.URL.build(
        scheme="redis",
        host=redis.get_container_host_ip(),
        port=redis.get_exposed_port(REDIS_PORT),
        path=f"/{REDIS_NAME}",
    )

    monkeypatch.setenv("BROKER_URL", str(redis_url))
    monkeypatch.setenv("RESULT_BACKEND", str(redis_url))

    import steins_feed_tasks.etl

    with Session() as session:
        steins_feed_config.read_xml(session, config_file, user=None)

    assert isinstance(steins_feed_tasks.etl.parse_feeds, celery.Task)
    res = steins_feed_tasks.etl.parse_feeds.delay()
    assert isinstance(res, celery.result.AsyncResult)
    res.wait()

    with Session() as session:
        assert len(session.scalars(sqla.select(steins_feed_model.items.Item)).all()) == 1
