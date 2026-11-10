import fastapi.testclient
import pytest

import steins_feed_model.users

@pytest.fixture
def my_client(
    client: fastapi.testclient.TestClient,
    user: steins_feed_model.users.User,
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

def test_tags(
    my_client: fastapi.testclient.TestClient,
):
    response = my_client.get("/feeds/tags/")
    res = response.json()

    assert len(res) == 1
    assert res[0]["name"] == "news"

def test_languages(
    my_client: fastapi.testclient.TestClient,
):
    response = my_client.get("/feeds/languages/")
    res = response.json()

    assert len(res) == 1
    assert res[0] == "English"

def test_feed(
    my_client: fastapi.testclient.TestClient,
):
    response = my_client.get("/feeds/feed/1")
    res = response.json()

    assert res["title"] == "The Guardian"
    assert len(res["tags"]) == 1
    assert res["tags"][0]["name"] == "news"
