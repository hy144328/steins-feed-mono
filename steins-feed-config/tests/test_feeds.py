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

@pytest.fixture
def temp_dir() -> typing.Generator[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def temp_file(temp_dir: str) -> typing.Generator[typing.TextIO]:
    with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
        f.write("""
<root>
  <feed>
    <title>The Guardian</title>
    <link>https://www.theguardian.com/uk/rss</link>
    <lang>English</lang>
    <tag>dummy</tag>
    <tag>news</tag>
  </feed>
</root>
        """)

    with open(f.name, "r") as f:
        yield f

def test_read_xml(
    session: sqla_orm.Session,
    user: steins_feed_model.users.User,
    temp_dir: str,
    temp_file: typing.TextIO,
):
    steins_feed_config.read_xml(
        session,
        temp_file,
        user_name = "hansolo",
    )

    q = sqla.select(steins_feed_model.feeds.Feed)
    feeds = session.execute(q).scalars().all()

    assert len(feeds) == 1
    assert len(feeds[0].tags) == 2

def test_read_and_write_xml(
    session: sqla_orm.Session,
    user: steins_feed_model.users.User,
    temp_dir: str,
    temp_file: typing.TextIO,
):
    steins_feed_config.read_xml(
        session,
        temp_file,
        user_name = "hansolo",
    )

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

    feeds = root.xpath("feed")
    assert len(feeds) == 1

    feed = feeds[0]
    tags = feed.xpath("tag")
    assert len(tags) == 2
