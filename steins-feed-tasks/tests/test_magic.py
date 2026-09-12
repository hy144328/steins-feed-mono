import collections.abc
import os.path
import tempfile
import typing

import celery
import celery.result
import pytest
import sqlalchemy as sqla
import sqlalchemy.orm as sqla_orm
import testcontainers.core.container
import testcontainers.core.image
import testcontainers.core.network
import wiremock.testing.testcontainer
import yarl

import steins_feed_config
import steins_feed_model.base
import steins_feed_model.items
import steins_feed_model.users

from . import shared

DB_NAME = "steins.db"
RSS_HOST = "rss"
RSS_PATH = "/rss.xml"
RSS_PORT = 8080
VOLUME_PATH = "/usr/src/app/data"

@pytest.fixture
def volume() -> collections.abc.Generator[str]:
    with tempfile.TemporaryDirectory() as temp_dir:
        yield temp_dir

@pytest.fixture
def database(volume: str) -> str:
    return os.path.join(volume, DB_NAME)

@pytest.fixture
def engine(database: str) -> sqla.Engine:
    engine = sqla.create_engine(sqla.URL.create("sqlite", database=database))
    steins_feed_model.base.Base.metadata.create_all(engine)
    return engine

@pytest.fixture
def Session(engine: sqla.Engine) -> sqla_orm.sessionmaker[sqla_orm.Session]:
    return sqla_orm.sessionmaker(engine)

@pytest.fixture
def worker(
    network: testcontainers.core.network.Network,
    volume: str,
) -> collections.abc.Generator[testcontainers.core.container.DockerContainer]:
    redis_url = yarl.URL.build(
        scheme="redis",
        host=shared.REDIS_HOST,
        port=shared.REDIS_PORT,
        path=f"/{shared.REDIS_NAME}",
    )

    with testcontainers.core.image.DockerImage(
        "../",
        dockerfile_path="steins-feed-tasks/Dockerfile",
    ) as image:
        with testcontainers.core.container.DockerContainer(str(image)).with_envs(
            BROKER_URL=str(redis_url),
            DB_NAME=os.path.join(VOLUME_PATH, DB_NAME),
            MAGIC_FOLDER=VOLUME_PATH,
            RESULT_BACKEND=str(redis_url),
        ).with_network(
            network,
        ).with_volume_mapping(
            volume,
            VOLUME_PATH,
            mode="rw",
        ) as container:
            try:
                yield container
            finally:
                out, err = container.get_logs()

                print("worker stdout:")
                print(out.decode())

                print("worker stderr:")
                print(err.decode())

@pytest.fixture
def server(
    network: testcontainers.core.network.Network,
) -> collections.abc.Generator[testcontainers.core.container.DockerContainer]:
    with wiremock.testing.testcontainer.WireMockContainer(secure=False).with_mapping(
        "rss.json",
        {
            "request": {
                "method": "GET",
                "url": str(yarl.URL.build(path=RSS_PATH)),
            },
            "response": {
                "status": 200,
                "headers": {
                    "Content-Type": "application/rss+xml",
                },
                "body": """
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
    <item>
      <title>How the Other Half Hates review</title>
      <link>https://www.theguardian.com/stage/2026/aug/12/how-the-other-half-hates-review-old-vic-london-alan-ayckbourn-roger-allam</link>
      <description>The Old Vic, London</description>
      <pubDate>Wed, 12 Aug 2026 17:00:34 GMT</pubDate>
    </item>
  </channel>
</rss>
                """,
            },
        },
    ).with_network(
        network,
    ).with_network_aliases(
        RSS_HOST,
    ) as container:
        try:
            yield container
        finally:
            out, err = container.get_logs()

            print("server stdout:")
            print(out.decode())

            print("server stderr:")
            print(err.decode())

@pytest.fixture
def config_file() -> collections.abc.Generator[typing.TextIO]:
    rss_url = yarl.URL.build(
        scheme="http",
        host=RSS_HOST,
        port=RSS_PORT,
        path=RSS_PATH,
    )

    with tempfile.TemporaryDirectory() as temp_dir:
        with tempfile.NamedTemporaryFile("w", dir=temp_dir, delete=False) as f:
            f.write(f"""
<root>
  <feed>
    <title>The Guardian</title>
    <link>{rss_url}</link>
    <lang>English</lang>
  </feed>
</root>
            """)

        with open(f.name, "r") as f:
            yield f

@pytest.fixture
def etl(
    app,
    worker,
    server,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    config_file: typing.TextIO,
):
    import steins_feed_tasks.etl

    with Session() as session:
        steins_feed_config.read_xml(session, config_file, user=None)

    assert isinstance(steins_feed_tasks.etl.parse_feeds, celery.Task)
    res = steins_feed_tasks.etl.parse_feeds.delay()
    assert isinstance(res, celery.result.AsyncResult)

    res.wait(timeout=5)

@pytest.fixture
def user(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
) -> steins_feed_model.users.User:
    with Session(expire_on_commit=False) as session:
        with session.begin():
            user = steins_feed_model.users.User(
                name="",
                password="",
                email=""
            )
            session.add(user)

    return user

@pytest.fixture
def liked_item(
    etl,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    user: steins_feed_model.users.User,
) -> steins_feed_model.items.Item:
    with Session(expire_on_commit=False) as session:
        with session.begin():
            q = sqla.select(
                steins_feed_model.items.Item,
            ).where(
                steins_feed_model.items.Item.title.ilike("%love%")
            )
            item = session.scalars(q).one()

        with session.begin():
            like = steins_feed_model.items.Like(
                user_id=user.id,
                item_id=item.id,
                score=steins_feed_model.items.LikeStatus.UP,
            )
            session.add(like)

    return item

@pytest.fixture
def disliked_item(
    etl,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    user: steins_feed_model.users.User,
) -> steins_feed_model.items.Item:
    with Session(expire_on_commit=False) as session:
        with session.begin():
            q = sqla.select(
                steins_feed_model.items.Item,
            ).where(
                steins_feed_model.items.Item.title.ilike("%hate%")
            )
            item = session.scalars(q).one()

        with session.begin():
            dislike = steins_feed_model.items.Like(
                user_id=user.id,
                item_id=item.id,
                score=steins_feed_model.items.LikeStatus.DOWN,
            )
            session.add(dislike)

    return item

def test_train_classifier(
    volume: str,
    user: steins_feed_model.users.User,
    liked_item: steins_feed_model.items.Item,
    disliked_item: steins_feed_model.items.Item,
):
    import steins_feed_tasks.magic

    assert isinstance(steins_feed_tasks.magic.train_classifier, celery.Task)
    res = steins_feed_tasks.magic.train_classifier.delay(
        user_id=user.id,
        lang=steins_feed_model.feeds.Language.ENGLISH,
    )
    assert isinstance(res, celery.result.AsyncResult)

    res.wait(timeout=10)

    classifier_path = os.path.join(
        volume,
        str(user.id),
        f"{steins_feed_model.feeds.Language.ENGLISH}.pickle",
    )
    assert os.path.exists(classifier_path)

@pytest.fixture
def classifier(
    user: steins_feed_model.users.User,
    liked_item: steins_feed_model.items.Item,
    disliked_item: steins_feed_model.items.Item,
):
    import steins_feed_tasks.magic

    assert isinstance(steins_feed_tasks.magic.train_classifier, celery.Task)
    res = steins_feed_tasks.magic.train_classifier.delay(
        user_id=user.id,
        lang=steins_feed_model.feeds.Language.ENGLISH,
    )
    assert isinstance(res, celery.result.AsyncResult)

    res.wait(timeout=10)

def test_calculate_scores(
    classifier,
    user: steins_feed_model.users.User,
    liked_item: steins_feed_model.items.Item,
    disliked_item: steins_feed_model.items.Item,
):
    import steins_feed_tasks.magic

    assert isinstance(steins_feed_tasks.magic.calculate_scores, celery.Task)
    res = steins_feed_tasks.magic.calculate_scores.delay(
        item_ids=[liked_item.id, disliked_item.id],
        user_id=user.id,
        lang=steins_feed_model.feeds.Language.ENGLISH,
    )
    assert isinstance(res, celery.result.AsyncResult)

    scores = res.get(timeout=5)
    assert scores[0][0] == liked_item.id and scores[0][1] > 0
    assert scores[1][0] == disliked_item.id and scores[1][1] < 0

def test_update_scores(
    classifier,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    user: steins_feed_model.users.User,
    liked_item: steins_feed_model.items.Item,
    disliked_item: steins_feed_model.items.Item,
):
    import steins_feed_tasks.magic

    assert isinstance(steins_feed_tasks.magic.calculate_scores, celery.Task)
    res = steins_feed_tasks.magic.calculate_scores.delay(
        item_ids=[liked_item.id, disliked_item.id],
        user_id=user.id,
        lang=steins_feed_model.feeds.Language.ENGLISH,
    )
    assert isinstance(res, celery.result.AsyncResult)

    scores = res.get(timeout=5)

    assert isinstance(steins_feed_tasks.magic.update_scores, celery.Task)
    res = steins_feed_tasks.magic.update_scores.delay(
        scores,
        user_id=user.id,
    )
    assert isinstance(res, celery.result.AsyncResult)

    res.wait(timeout=5)

    with Session.begin() as session:
        q = sqla.select(
            steins_feed_model.items.Magic,
        ).where(
            steins_feed_model.items.Magic.item_id == liked_item.id,
        )
        item = session.scalars(q).one()
        assert item.score > 0

        q = sqla.select(
            steins_feed_model.items.Magic,
        ).where(
            steins_feed_model.items.Magic.item_id == disliked_item.id,
        )
        item = session.scalars(q).one()
        assert item.score < 0

def test_analyze_text_like(
    classifier,
    user: steins_feed_model.users.User,
    liked_item: steins_feed_model.items.Item,
):
    import steins_feed_tasks.magic

    assert isinstance(steins_feed_tasks.magic.analyze_text, celery.Task)
    res = steins_feed_tasks.magic.analyze_text.delay(
        liked_item.title,
        user_id=user.id,
        lang=steins_feed_model.feeds.Language.ENGLISH,
    )
    assert isinstance(res, celery.result.AsyncResult)

    scores = res.get(timeout=5)
    score = next(score_it for score_it in scores if score_it[0] == "Loves")
    assert score[2] > 0

def test_analyze_text_dislike(
    classifier,
    user: steins_feed_model.users.User,
    disliked_item: steins_feed_model.items.Item,
):
    import steins_feed_tasks.magic

    assert isinstance(steins_feed_tasks.magic.analyze_text, celery.Task)
    res = steins_feed_tasks.magic.analyze_text.delay(
        disliked_item.title,
        user_id=user.id,
        lang=steins_feed_model.feeds.Language.ENGLISH,
    )
    assert isinstance(res, celery.result.AsyncResult)

    scores = res.get(timeout=5)
    score = next(score_it for score_it in scores if score_it[0] == "Hates")
    assert score[2] < 0
