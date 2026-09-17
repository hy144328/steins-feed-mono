import collections.abc
import datetime

import fastapi.testclient
import pytest
import sqlalchemy.orm as sqla_orm
import testcontainers.core.container

import steins_feed_model.items
import steins_feed_model.users

@pytest.fixture
def my_client(
    client: fastapi.testclient.TestClient,
) -> fastapi.testclient.TestClient:
    response = client.post(
        "/token",
        data={
            "username": "hansolo",
            "password": "obiwan",
        },
    )
    res = response.json()
    token = res["access_token"]

    client.headers.update({"Authorization": f"Bearer {token}"})
    return client

def test_last_updated(
    my_client: fastapi.testclient.TestClient,
    user: steins_feed_model.users.User,
):
    response = my_client.get("/items/last_updated")
    res = response.json()

    assert datetime.datetime.fromisoformat(res) == datetime.datetime(2026, 8, 12, 17, 0, 34, tzinfo=datetime.timezone.utc)

@pytest.fixture
def my_liked_item(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    liked_item: steins_feed_model.items.Item,
) -> collections.abc.Generator[steins_feed_model.items.Item]:
    yield liked_item

    with Session.begin() as session:
        item = session.get_one(steins_feed_model.items.Item, liked_item.id)
        item.likes[0].score = steins_feed_model.items.LikeStatus.UP

@pytest.fixture
def my_disliked_item(
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    disliked_item: steins_feed_model.items.Item,
) -> collections.abc.Generator[steins_feed_model.items.Item]:
    yield disliked_item

    with Session.begin() as session:
        item = session.get_one(steins_feed_model.items.Item, disliked_item.id)
        item.likes[0].score = steins_feed_model.items.LikeStatus.DOWN

def test_like(
    my_client: fastapi.testclient.TestClient,
    Session: sqla_orm.sessionmaker[sqla_orm.Session],
    my_liked_item: steins_feed_model.items.Item,
    my_disliked_item: steins_feed_model.items.Item,
):
    with Session() as session:
        for status_it in steins_feed_model.items.LikeStatus:
            response = my_client.put(
                "/items/like/",
                params={
                    "item_id": my_liked_item.id,
                    "score": status_it.value,
                },
            )
            assert response.status_code == 200

            with session.begin():
                assert session.get_one(
                    steins_feed_model.items.Item,
                    my_liked_item.id,
                ).likes[0].score == status_it

        for status_it in steins_feed_model.items.LikeStatus:
            response = my_client.put(
                "/items/like/",
                params={
                    "item_id": my_disliked_item.id,
                    "score": status_it.value,
                },
            )
            assert response.status_code == 200

            with session.begin():
                assert session.get_one(
                    steins_feed_model.items.Item,
                    my_disliked_item.id,
                ).likes[0].score == status_it

def test_analyze_title(
    my_client: fastapi.testclient.TestClient,
    worker: testcontainers.core.container.DockerContainer,
    classifier,
    my_liked_item: steins_feed_model.items.Item,
    my_disliked_item: steins_feed_model.items.Item,
):
    response = my_client.get(
        "/items/analyze_title",
        params = {
            "item_id": my_liked_item.id,
        },
    )
    res = response.json()
    assert next(e for e in res if e[0] == "Loves")[2] > 0

    response = my_client.get("/items/analyze_title", params={"item_id": my_disliked_item.id})
    res = response.json()
    assert next(e for e in res if e[0] == "Hates")[2] < 0

def test_items_classic(
    my_client: fastapi.testclient.TestClient,
    worker: testcontainers.core.container.DockerContainer,
    classifier,
    my_liked_item: steins_feed_model.items.Item,
    my_disliked_item: steins_feed_model.items.Item,
):
    response = my_client.get(
        "/items/",
        params={
            "dt_from": datetime.datetime(2026, 8, 12, 17, tzinfo=datetime.timezone.utc).isoformat(),
            "dt_to": datetime.datetime(2026, 8, 12, 18, tzinfo=datetime.timezone.utc).isoformat(),
        },
    )
    res = response.json()
    assert len(res) == 2

    assert res[0]["title"] == my_disliked_item.title
    assert res[0]["magic"] is None
    assert res[1]["title"] == my_liked_item.title
    assert res[1]["magic"] is None

def test_items_magic(
    my_client: fastapi.testclient.TestClient,
    worker: testcontainers.core.container.DockerContainer,
    classifier,
    my_liked_item: steins_feed_model.items.Item,
    my_disliked_item: steins_feed_model.items.Item,
):
    import steins_feed_api.routers.items

    response = my_client.get(
        "/items/",
        params={
            "dt_from": datetime.datetime(2026, 8, 12, 17, tzinfo=datetime.timezone.utc).isoformat(),
            "dt_to": datetime.datetime(2026, 8, 12, 18, tzinfo=datetime.timezone.utc).isoformat(),
            "wall_mode": steins_feed_api.routers.items.WallMode.MAGIC.value,
        },
    )
    res = response.json()
    assert len(res) == 2

    assert res[0]["title"] == my_liked_item.title
    assert res[0]["magic"] > 0
    assert res[1]["title"] == my_disliked_item.title
    assert res[1]["magic"] < 0

def test_items_random(
    my_client: fastapi.testclient.TestClient,
    worker: testcontainers.core.container.DockerContainer,
    classifier,
    my_liked_item: steins_feed_model.items.Item,
    my_disliked_item: steins_feed_model.items.Item,
):
    import steins_feed_api.routers.items

    response = my_client.get(
        "/items/",
        params={
            "dt_from": datetime.datetime(2026, 8, 12, 17, tzinfo=datetime.timezone.utc).isoformat(),
            "dt_to": datetime.datetime(2026, 8, 12, 18, tzinfo=datetime.timezone.utc).isoformat(),
            "wall_mode": steins_feed_api.routers.items.WallMode.RANDOM.value,
        },
    )
    res = response.json()
    assert len(res) <= 10

    assert res[0]["title"] in {my_liked_item.title, my_disliked_item.title}
    assert res[0]["magic"] is None
    assert res[1]["title"] in {my_liked_item.title, my_disliked_item.title}
    assert res[1]["magic"] is None

def test_items_surprise(
    my_client: fastapi.testclient.TestClient,
    worker: testcontainers.core.container.DockerContainer,
    classifier,
    my_liked_item: steins_feed_model.items.Item,
    my_disliked_item: steins_feed_model.items.Item,
):
    import steins_feed_api.routers.items

    response = my_client.get(
        "/items/",
        params={
            "dt_from": datetime.datetime(2026, 8, 12, 17, tzinfo=datetime.timezone.utc).isoformat(),
            "dt_to": datetime.datetime(2026, 8, 12, 18, tzinfo=datetime.timezone.utc).isoformat(),
            "wall_mode": steins_feed_api.routers.items.WallMode.SURPRISE.value,
        },
    )
    res = response.json()
    assert len(res) <= 10

    assert res[0]["title"] in {my_liked_item.title, my_disliked_item.title}
    assert res[0]["magic"] is not None
    assert res[1]["title"] in {my_liked_item.title, my_disliked_item.title}
    assert res[1]["magic"] is not None
