import collections.abc
import tempfile
import typing

import aiohttp
import aioresponses
import pytest
import pytest_asyncio
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

@pytest_asyncio.fixture
async def client() -> collections.abc.AsyncGenerator[aiohttp.ClientSession]:
    with aioresponses.aioresponses() as m:
        m.get(
            "https://www.theguardian.com/uk/rss",
            status = 200,
            body = b"""
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
        )

        async with aiohttp.ClientSession() as client:
            yield client

@pytest.fixture
def temp_file() -> collections.abc.Generator[typing.TextIO]:
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

@pytest.mark.asyncio
async def test_parse_feeds(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    client: aiohttp.ClientSession,
    temp_file: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, temp_file, user=None)

    await steins_feed_etl.parse_feeds(Session, client)

    q = sqla.select(steins_feed_model.items.Item)
    res = session.scalars(q).all()
    assert len(res) == 1

@pytest_asyncio.fixture
async def client_long() -> collections.abc.AsyncGenerator[aiohttp.ClientSession]:
    with aioresponses.aioresponses() as m:
        m.get(
            "https://www.theguardian.com/uk/rss",
            status = 200,
            body = b"""
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
        )
        m.get(
            "https://www.theguardian.com/uk/culture/rss",
            status = 200,
            body = b"""
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
        )

        async with aiohttp.ClientSession() as client:
            yield client

@pytest.fixture
def temp_file_long() -> collections.abc.Generator[typing.TextIO]:
    with tempfile.TemporaryDirectory() as temp_dir:
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
async def test_parse_feeds_long(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    client_long: aiohttp.ClientSession,
    temp_file_long: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, temp_file_long, user=None)

    await steins_feed_etl.parse_feeds(Session, client_long, batch_size=1)

    q = sqla.select(steins_feed_model.items.Item)
    res = session.scalars(q).all()
    assert len(res) == 2

@pytest.mark.asyncio
async def test_parse_feeds_pattern(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    client_long: aiohttp.ClientSession,
    temp_file_long: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, temp_file_long, user=None)

    await steins_feed_etl.parse_feeds(Session, client_long, title_pattern="Culture")

    q = sqla.select(steins_feed_model.items.Item)
    res = session.scalars(q).all()
    assert len(res) == 1
