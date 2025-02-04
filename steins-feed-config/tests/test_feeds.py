import tempfile
import typing

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
    engine = steins_feed_model.EngineFactory.create_engine()
    steins_feed_model.base.Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(
    engine: sqla.engine.Engine,
) -> typing.Generator[sqla_orm.Session]:
    with sqla_orm.Session(engine) as session:
        yield session

@pytest.fixture
def user(
    session: sqla_orm.Session,
) -> steins_feed_model.users.User:
    user = steins_feed_model.users.User(
        name = "hansolo",
        password = "",
        email = "hans.yu@outlook.de",
    )
    session.add(user)
    session.commit()

    return user

def test_read_and_write_xml(
    session: sqla_orm.Session,
    user: steins_feed_model.users.User,
):
    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
            f.write("""
<root>
  <feed>
    <title>The Guardian</title>
    <link>https://www.theguardian.com/uk/rss</link>
    <lang>English</lang>
    <tag>News</tag>
  </feed>
</root>
            """)

        with open(f.name, "r") as f:
            steins_feed_config.read_xml(
                session,
                f,
                user_name = "hansolo",
            )

        q = sqla.select(steins_feed_model.feeds.Feed)
        res = session.execute(q).scalars().all()
        assert len(res) == 1

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
