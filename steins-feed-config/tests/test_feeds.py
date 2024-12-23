import tempfile

import lxml.etree
import pytest
import sqlalchemy as sqla

import steins_feed_model
import steins_feed_model.feeds

@pytest.fixture
def engine() -> sqla.engine.Engine:
    return steins_feed_model.EngineFactory.get_or_create_engine()

@pytest.fixture
def metadata(engine: sqla.engine.Engine) -> sqla.MetaData:
    return steins_feed_model.EngineFactory.create_metadata(engine)

def test_read_and_write_xml(
    engine: sqla.engine.Engine,
    metadata: sqla.MetaData,
):
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
                steins_feed_model.feeds.read_xml(
                    conn,
                    metadata,
                    f,
                )

        t = metadata.tables["Feeds"]
        q = sqla.select(t)
        with engine.connect() as conn:
            res = conn.execute(q).fetchall()

        assert len(res) == 1

        with engine.connect() as conn:
            with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
                steins_feed_model.feeds.write_xml(
                    conn,
                    metadata,
                    f,
                )

        with open(f.name, "r") as f:
            tree = lxml.etree.parse(f)
            root = tree.getroot()

        assert len(root.xpath("feed")) == 1
