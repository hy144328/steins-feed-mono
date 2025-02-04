import datetime
import tempfile
import typing

import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import pytest

import steins_feed_config
import steins_feed_magic.db
import steins_feed_model
import steins_feed_model.base
import steins_feed_model.items

@pytest.fixture
def engine() -> sqla.engine.Engine:
    engine = steins_feed_model.EngineFactory.create_engine()
    steins_feed_model.base.Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def session(engine: sqla.engine.Engine) -> typing.Generator[sqla_orm.Session]:
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

def test_db(
    session: sqla_orm.Session,
    user: steins_feed_model.users.User,
    temp_file: typing.TextIO,
):
    steins_feed_config.read_xml(
        session,
        temp_file,
        user_id = user.id,
    )

    item = steins_feed_model.items.Item(
        title = "Donald Trump",
        link = "https://donald.trump",
        published = datetime.datetime(2025, 3, 1),
        feed_id = 1,
    )
    session.add(item)
    session.commit()

    like = steins_feed_model.items.Like(
        user_id = user.id,
        item_id = item.id,
        score = steins_feed_model.items.LikeStatus.UP,
    )
    session.add(like)
    session.commit()

    up = steins_feed_model.items.Magic(
        user_id = user.id,
        item_id = item.id,
        score = steins_feed_model.items.LikeStatus.UP,
    )
    session.add(up)
    session.commit()

    item = steins_feed_model.items.Item(
        title = "Joe Biden",
        link = "https://joe.biden",
        published = datetime.datetime(2025, 3, 1),
        feed_id = 1,
    )
    session.add(item)
    session.commit()

    dislike = steins_feed_model.items.Like(
        user_id = user.id,
        item_id = item.id,
        score = steins_feed_model.items.LikeStatus.DOWN,
    )
    session.add(dislike)
    session.commit()

    down = steins_feed_model.items.Magic(
        user_id = user.id,
        item_id = item.id,
        score = steins_feed_model.items.LikeStatus.DOWN,
    )
    session.add(down)
    session.commit()

    liked_items = steins_feed_magic.db.liked_items(
        session,
        user_id = user.id,
        lang = steins_feed_model.feeds.Language.ENGLISH,
    )
    assert len(liked_items) == 1

    disliked_items = steins_feed_magic.db.disliked_items(
        session,
        user_id = user.id,
        lang = steins_feed_model.feeds.Language.ENGLISH,
    )
    assert len(disliked_items) == 1

    assert len(session.execute(sqla.select(steins_feed_model.items.Magic)).all()) == 2
    steins_feed_magic.db.reset_magic(
        session,
        user_id = user.id,
        lang = steins_feed_model.feeds.Language.ENGLISH,
    )
    assert len(session.execute(sqla.select(steins_feed_model.items.Magic)).all()) == 0
