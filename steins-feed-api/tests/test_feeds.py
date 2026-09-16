import fastapi.testclient

import steins_feed_model.users

def test_tags(
    client: fastapi.testclient.TestClient,
    user: steins_feed_model.users.User,
):
    response = client.post(
        "/token",
        data={
            "username": "hansolo",
            "password": "obiwan",
        },
    )
    res = response.json()
    token = res["access_token"]

    response = client.get(
        "/feeds/tags/",
        headers = {
            "Authorization": f"Bearer {token}",
        },
    )
    res = response.json()

    assert len(res) == 1
    assert res[0]["name"] == "news"

def test_languages(
    client: fastapi.testclient.TestClient,
    user: steins_feed_model.users.User,
):
    response = client.post(
        "/token",
        data={
            "username": "hansolo",
            "password": "obiwan",
        },
    )
    res = response.json()
    token = res["access_token"]

    response = client.get(
        "/feeds/languages/",
        headers = {
            "Authorization": f"Bearer {token}",
        },
    )
    res = response.json()

    assert len(res) == 1
    assert res[0] == "English"

def test_feed(
    client: fastapi.testclient.TestClient,
):
    response = client.post(
        "/token",
        data={
            "username": "hansolo",
            "password": "obiwan",
        },
    )
    res = response.json()
    token = res["access_token"]

    response = client.get(
        "/feeds/feed/1",
        headers = {
            "Authorization": f"Bearer {token}",
        },
    )
    res = response.json()

    assert res["title"] == "The Guardian"
    assert len(res["tags"]) == 1
    assert res["tags"][0]["name"] == "news"
