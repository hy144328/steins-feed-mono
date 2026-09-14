import fastapi.testclient

def test(
    client: fastapi.testclient.TestClient,
):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Hello world."}
