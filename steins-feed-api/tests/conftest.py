import collections.abc
import os
import tempfile
import typing

import aiohttp
import aioresponses
import celery
import celery.result
import fastapi.testclient
import pwdlib
import pytest
import pytest_asyncio
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import testcontainers.core.container
import testcontainers.core.image
import testcontainers.core.network
import testcontainers.redis
import yarl

import steins_feed_config
import steins_feed_etl
import steins_feed_magic.classify
import steins_feed_magic.db
import steins_feed_magic.io
import steins_feed_magic.parse

import steins_feed_model.base

DB_NAME = "steins.db"
DEV_USER = "hansolo"
DEV_PASS = "obiwan"
DEV_MAIL = "death@star.universe"
REDIS_HOST = "redis"
REDIS_NAME = "0"
REDIS_PORT = 6379
VOLUME_PATH = "/usr/src/app/data"

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
        REDIS_HOST,
    ).with_exposed_ports(
        REDIS_PORT,
    ) as container:
        try:
            yield container
        finally:
            out, err = container.get_logs()

            print("Redis stdout:")
            print(out.decode())

            print("Redis stderr:")
            print(err.decode())

@pytest.fixture(scope="session")
def volume() -> collections.abc.Generator[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture(scope="session")
def database(volume: str) -> str:
    return os.path.join(volume, DB_NAME)

@pytest.fixture(scope="session")
def engine(database: str) -> sqla.Engine:
    engine = sqla.create_engine(sqla.URL.create("sqlite", database=database))
    steins_feed_model.base.Base.metadata.create_all(engine)
    return engine

@pytest.fixture(scope="session")
def Session(engine: sqla.Engine) -> sqla_orm.sessionmaker[sqla_orm.Session]:
    return sqla_orm.sessionmaker(engine)

@pytest.fixture(scope="session")
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
            MAGIC_FOLDER=VOLUME_PATH,
            RESULT_BACKEND=str(redis_url),
        ).with_network(
            network,
        ).with_volume_mapping(
            volume,
            VOLUME_PATH,
            mode="rw",
        ) as container:
            try:
                yield container
            finally:
                out, err = container.get_logs()

                print("worker stdout:")
                print(out.decode())

                print("worker stderr:")
                print(err.decode())

@pytest_asyncio.fixture(scope="session")
async def rss_client() -> collections.abc.AsyncGenerator[aiohttp.ClientSession]:
    with aioresponses.aioresponses() as m:
        m.get(
            "https://www.theguardian.com/uk/rss",
            status = 200,
            body = """
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
    <item>
      <title>How the Other Half Hates review</title>
      <link>https://www.theguardian.com/stage/2026/aug/12/how-the-other-half-hates-review-old-vic-london-alan-ayckbourn-roger-allam</link>
      <description>The Old Vic, London</description>
      <pubDate>Wed, 12 Aug 2026 17:00:34 GMT</pubDate>
    </item>
  </channel>
</rss>
            """,
        )

        async with aiohttp.ClientSession() as client:
            yield client

@pytest.fixture(scope="session")
def config_file() -> collections.abc.Generator[typing.TextIO]:
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
            f.write("""
<root>
  <feed>
    <title>The Guardian</title>
    <link>https://www.theguardian.com/uk/rss</link>
    <lang>English</lang>
  </feed>
</root>
            """)

        with open(f.name, "r") as f:
            yield f

@pytest_asyncio.fixture(scope="session")
async def etl(
    rss_client: aiohttp.ClientSession,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    config_file: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, config_file, user=None)

    await steins_feed_etl.parse_feeds(Session, rss_client)

@pytest.fixture(scope="session")
def user(
    etl,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
) -> steins_feed_model.users.User:
    password_hash = pwdlib.PasswordHash.recommended()

    with Session() as session:
        user = steins_feed_model.users.User(
            name=DEV_USER,
            password=password_hash.hash(DEV_PASS),
            email=DEV_MAIL,
        )
        with session.begin():
            session.add(user)

        with session.begin():
            feed = session.scalars(sqla.select(steins_feed_model.feeds.Feed)).one()
            feed.users.append(user)

            tag = steins_feed_model.feeds.Tag(
                user_id = user.id,
                name = "news",
            )
            feed.tags.append(tag)

        with session.begin():
            session.refresh(user)
            session.expunge(user)
            return user

@pytest.fixture(scope="session")
def liked_item(
    etl,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    user: steins_feed_model.users.User,
) -> steins_feed_model.items.Item:
    with Session() as session:
        with session.begin():
            q = sqla.select(
                steins_feed_model.items.Item,
            ).where(
                steins_feed_model.items.Item.title.ilike("%love%")
            )
            item = session.scalars(q).one()

            like = steins_feed_model.items.Like(
                user_id=user.id,
                item_id=item.id,
                score=steins_feed_model.items.LikeStatus.UP,
            )
            session.add(like)

        with session.begin():
            session.refresh(item)
            session.expunge(item)
            return item

@pytest.fixture(scope="session")
def disliked_item(
    etl,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    user: steins_feed_model.users.User,
) -> steins_feed_model.items.Item:
    with Session() as session:
        with session.begin():
            q = sqla.select(
                steins_feed_model.items.Item,
            ).where(
                steins_feed_model.items.Item.title.ilike("%hate%")
            )
            item = session.scalars(q).one()

            dislike = steins_feed_model.items.Like(
                user_id=user.id,
                item_id=item.id,
                score=steins_feed_model.items.LikeStatus.DOWN,
            )
            session.add(dislike)

        with session.begin():
            session.refresh(item)
            session.expunge(item)
            return item

@pytest.fixture(scope="session")
def classifier(
    volume: str,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    user: steins_feed_model.users.User,
    liked_item: steins_feed_model.items.Item,
    disliked_item: steins_feed_model.items.Item,
):
    clf = steins_feed_magic.classify.build_classifier(steins_feed_model.feeds.Language.ENGLISH)

    with Session() as session:
        with session.begin():
            liked_items = [
                steins_feed_magic.parse.text_content(item_it.title)
                for item_it in steins_feed_magic.db.liked_items(session, user.id, steins_feed_model.feeds.Language.ENGLISH)
            ]
            disliked_items = [
                steins_feed_magic.parse.text_content(item_it.title)
                for item_it in steins_feed_magic.db.disliked_items(session, user.id, steins_feed_model.feeds.Language.ENGLISH)
            ]

        steins_feed_magic.classify.fit_classifier(
            clf,
            liked_items = liked_items,
            disliked_items = disliked_items,
        )
        steins_feed_magic.io.write_classifier(
            clf,
            volume,
            user_id = user.id,
            lang = steins_feed_model.feeds.Language.ENGLISH,
            force = True,
        )

        with session.begin():
            steins_feed_magic.db.reset_magic(
                session,
                user_id = user.id,
                lang = steins_feed_model.feeds.Language.ENGLISH,
            )

@pytest.fixture
def client(
    monkeypatch: pytest.MonkeyPatch,
    database: str,
    redis: testcontainers.redis.RedisContainer,
) -> fastapi.testclient.TestClient:
    redis_url = yarl.URL.build(
        scheme="redis",
        host=redis.get_container_host_ip(),
        port=redis.get_exposed_port(REDIS_PORT),
        path=f"/{REDIS_NAME}",
    )

    monkeypatch.setenv("BROKER_URL", str(redis_url))
    monkeypatch.setenv("DB_NAME", database)
    monkeypatch.setenv("RESULT_BACKEND", str(redis_url))
    monkeypatch.setenv("SECRET_KEY", "76f615f3b628e194387f26d7adbf2632dd290c8be7d098d85b9f6c6a0ff0b1df")

    import steins_feed_api

    return fastapi.testclient.TestClient(steins_feed_api.app)
