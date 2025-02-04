import tempfile

import lxml.etree
import pytest
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm

import steins_feed_config
import steins_feed_model
import steins_feed_model.base
import steins_feed_model.users

@pytest.fixture
def engine() -> sqla.engine.Engine:
    return steins_feed_model.EngineFactory.create_engine()

def test_read_and_write_xml(engine: sqla.engine.Engine):
    steins_feed_model.base.Base.metadata.create_all(engine)

    user = steins_feed_model.users.User(
        name = "hansolo",
        password = "",
        email = "hans.yu@outlook.de",
    )

    q = sqla.insert(
        steins_feed_model.users.User,
    ).values(
        name = user.name,
        password = user.password,
        email = user.email,
    )

    with sqla_orm.Session(engine) as session:
        session.execute(q)
        session.commit()

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
                steins_feed_config.read_xml(
                    session,
                    f,
                    user_name = "hansolo",
                )

        q = sqla.select(steins_feed_model.feeds.Feed)
        with sqla_orm.Session(engine) as session:
            res = session.execute(q).scalars().all()
            assert len(res) == 1

        with sqla_orm.Session(engine) as session:
            with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
                pass

            with open(f.name, "w") as f:
                steins_feed_config.write_xml(
                    session,
                    f,
                    user_name = "hansolo",
                )

        with open(f.name, "r") as f:
            tree = lxml.etree.parse(f)
            root = tree.getroot()

        assert len(root.xpath("feed")) == 1
