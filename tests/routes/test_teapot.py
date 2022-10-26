def test_teapot(api_client):
    response = api_client.get("/teapot")
    assert response.status_code == 418
    result = response.json()
    assert result == "I'm a teapot"
