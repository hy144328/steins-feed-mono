import collections.abc
import tempfile
import typing

import aiohttp
import aiohttp.test_utils
import aiohttp.web
import pytest
import pytest_aiohttp.plugin
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

async def feed(request: aiohttp.web.Request) -> aiohttp.web.Response:
    return aiohttp.web.Response(
        text="""
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

@pytest.fixture
def server() -> aiohttp.web.Application:
    app = aiohttp.web.Application()
    app.router.add_get("/rss", feed)
    return app

@pytest_asyncio.fixture
async def client(
    aiohttp_client: pytest_aiohttp.plugin.AiohttpClient,
    server: aiohttp.web.Application,
) -> aiohttp.test_utils.TestClient[aiohttp.web.Request, aiohttp.web.Application]:
    return await aiohttp_client(server)

@pytest.fixture
def config_file(
    client: aiohttp.test_utils.TestClient[aiohttp.web.Request, aiohttp.web.Application],
) -> collections.abc.Generator[typing.TextIO]:
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
            f.write(f"""
<root>
  <feed>
    <title>The Guardian</title>
    <link>{client.make_url("/rss")}</link>
    <lang>English</lang>
  </feed>
</root>
            """)

        with open(f.name, "r") as f:
            yield f

@pytest.mark.asyncio
async def test_parse_feeds(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    client: aiohttp.test_utils.TestClient[aiohttp.web.Request, aiohttp.web.Application],
    config_file: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, config_file, user=None)

    await steins_feed_etl.parse_feeds(Session, client.session)

    q = sqla.select(steins_feed_model.items.Item)
    res = session.scalars(q).all()
    assert len(res) == 1

async def feed_long(request: aiohttp.web.Request) -> aiohttp.web.Response:
    return aiohttp.web.Response(
        text="""
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

async def feed_long_culture(request: aiohttp.web.Request) -> aiohttp.web.Response:
    return aiohttp.web.Response(
        text="""
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

@pytest.fixture
def server_long() -> aiohttp.web.Application:
    app = aiohttp.web.Application()
    app.router.add_get("/rss", feed_long)
    app.router.add_get("/culture/rss", feed_long_culture)
    return app

@pytest_asyncio.fixture
async def client_long(
    aiohttp_client: pytest_aiohttp.plugin.AiohttpClient,
    server_long: aiohttp.web.Application,
) -> aiohttp.test_utils.TestClient[aiohttp.web.Request, aiohttp.web.Application]:
    return await aiohttp_client(server_long)

@pytest.fixture
def config_file_long(
    client_long: aiohttp.test_utils.TestClient[aiohttp.web.Request, aiohttp.web.Application],
) -> collections.abc.Generator[typing.TextIO]:
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
            f.write(f"""
<root>
  <feed>
    <title>The Guardian</title>
    <link>{client_long.make_url("/rss")}</link>
    <lang>English</lang>
  </feed>
  <feed>
    <title>The Guardian Culture</title>
    <link>{client_long.make_url("/culture/rss")}</link>
    <lang>English</lang>
  </feed>
  <feed>
    <title>The Guardian Lifestyle</title>
    <link>{client_long.make_url("/lifeandstyle/rss")}</link>
    <lang>English</lang>
  </feed>
  <feed>
    <title>The Guardian Opinion</title>
    <link>{client_long.make_url("/commentisfree/rss")}</link>
    <lang>English</lang>
  </feed>
  <feed>
    <title>The Guardian Sport</title>
    <link>{client_long.make_url("/sport/rss")}</link>
    <lang>English</lang>
  </feed>
</root>
            """)

        with open(f.name, "r") as f:
            yield f

@pytest.mark.asyncio
async def test_parse_feeds_long(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    client_long: aiohttp.test_utils.TestClient[aiohttp.web.Request, aiohttp.web.Application],
    config_file_long: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, config_file_long, user=None)

    await steins_feed_etl.parse_feeds(Session, client_long.session, batch_size=1)

    q = sqla.select(steins_feed_model.items.Item)
    res = session.scalars(q).all()
    assert len(res) == 2

@pytest.mark.asyncio
async def test_parse_feeds_pattern(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    client_long: aiohttp.test_utils.TestClient[aiohttp.web.Request, aiohttp.web.Application],
    config_file_long: typing.TextIO,
):
    with Session() as session:
        steins_feed_config.read_xml(session, config_file_long, user=None)

    await steins_feed_etl.parse_feeds(Session, client_long.session, title_pattern="Culture")

    q = sqla.select(steins_feed_model.items.Item)
    res = session.scalars(q).all()
    assert len(res) == 1
