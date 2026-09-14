import fastapi.testclient

import steins_feed_model.users

def test_root(
    client: fastapi.testclient.TestClient,
):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world."}

def test_token(
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
    assert response.status_code == 200

    res = response.json()
    assert "access_token" in res
    assert res["token_type"] == "bearer"
