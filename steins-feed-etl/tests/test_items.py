import tempfile

import aiohttp
import pytest
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_config.feeds
import steins_feed_etl.items
import steins_feed_model
import steins_feed_model.base

@pytest.fixture
def engine() -> sqla.engine.Engine:
    return steins_feed_model.EngineFactory.create_engine()

@pytest.mark.asyncio
async def test_parser_feeds(
    engine: sqla.engine.Engine,
):
    steins_feed_model.base.Base.metadata.create_all(engine)

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

        with sqla_orm.Session(engine) as session:
            with open(f.name, "r") as f:
                steins_feed_config.feeds.read_xml(session, f)

    with sqla_orm.Session(engine) as session:
        async with aiohttp.ClientSession() as client:
            await steins_feed_etl.items.parse_feeds(session, client)

    q = sqla.select(steins_feed_model.items.Item)
    with sqla_orm.Session(engine) as session:
        res = session.execute(q).scalars().all()
        assert len(res) > 0
