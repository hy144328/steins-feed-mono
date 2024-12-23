import tempfile

import lxml.etree
import pytest
import sqlalchemy as sqla

import steins_feed_config.feeds
import steins_feed_model
import steins_feed_model.schema
import steins_feed_model.schema.feeds

@pytest.fixture
def engine() -> sqla.engine.Engine:
    engine = steins_feed_model.EngineFactory.get_or_create_engine()

    with engine.connect() as conn:
        steins_feed_model.schema.create_schema(conn)

    return engine

def test_read_and_write_xml(engine: sqla.engine.Engine):
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

        with engine.connect() as conn:
            with open(f.name, "r") as f:
                steins_feed_config.feeds.read_xml(
                    conn,
                    f,
                )

        q = sqla.select(steins_feed_model.schema.feeds.t_feeds)
        with engine.connect() as conn:
            res = conn.execute(q).fetchall()

        assert len(res) == 1

        with engine.connect() as conn:
            with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
                steins_feed_config.feeds.write_xml(
                    conn,
                    f,
                )

        with open(f.name, "r") as f:
            tree = lxml.etree.parse(f)
            root = tree.getroot()

        assert len(root.xpath("feed")) == 1
