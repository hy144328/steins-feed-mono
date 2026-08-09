import collections.abc
import tempfile
import typing

import aiohttp
import pytest
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_config
import steins_feed_etl
import steins_feed_model
import steins_feed_model.base

@pytest.fixture
def engine() -> sqla.engine.Engine:
    engine = sqla.create_engine(sqla.URL.create("sqlite"))
    steins_feed_model.base.Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def Session(engine: sqla.engine.Engine) -> sqla_orm.sessionmaker[sqla_orm.Session]:
    return sqla_orm.sessionmaker(engine)

@pytest.fixture
def temp_dir() -> collections.abc.Generator[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def temp_file(temp_dir: str) -> collections.abc.Generator[typing.TextIO]:
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

@pytest.fixture
def temp_file_long(temp_dir: str) -> collections.abc.Generator[typing.TextIO]:
    with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
        f.write("""
<root>
  <feed>
    <title>The Guardian</title>
    <link>https://www.theguardian.com/uk/rss</link>
    <lang>English</lang>
  </feed>
  <feed>
    <title>The Guardian Culture</title>
    <link>https://www.theguardian.com/uk/culture/rss</link>
    <lang>English</lang>
  </feed>
  <feed>
    <title>The Guardian Lifestyle</title>
    <link>https://www.theguardian.com/uk/lifeandstyle/rss</link>
    <lang>English</lang>
  </feed>
  <feed>
    <title>The Guardian Opinion</title>
    <link>https://www.theguardian.com/uk/commentisfree/rss</link>
    <lang>English</lang>
  </feed>
  <feed>
    <title>The Guardian Sport</title>
    <link>https://www.theguardian.com/uk/sport/rss</link>
    <lang>English</lang>
  </feed>
</root>
        """)

    with open(f.name, "r") as f:
        yield f

@pytest.mark.asyncio
async def test_parse_feeds(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    temp_file: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, temp_file, user_id=None)

    async with aiohttp.ClientSession() as client:
        await steins_feed_etl.parse_feeds(Session, client)

    q = sqla.select(steins_feed_model.items.Item)
    res = session.execute(q).scalars().all()
    assert len(res) > 0

@pytest.mark.asyncio
async def test_parse_feeds_long(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    temp_file_long: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, temp_file_long, user_id=None)

    async with aiohttp.ClientSession() as client:
        await steins_feed_etl.parse_feeds(Session, client)

    q = sqla.select(steins_feed_model.items.Item)
    res = session.execute(q).scalars().all()
    assert len(res) > steins_feed_etl.BATCH_SIZE

@pytest.mark.asyncio
async def test_parse_feeds_pattern(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    temp_file_long: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, temp_file_long, user_id=None)

    async with aiohttp.ClientSession() as client:
        await steins_feed_etl.parse_feeds(Session, client, title_pattern="Culture")

    q = sqla.select(steins_feed_model.items.Item)
    res = session.execute(q).scalars().all()
    assert len(res) > 0
