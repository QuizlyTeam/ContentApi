def test_get_categories(mock_request, settings, api_client):
    categories = {"Arts & Literature": 1, "Film & TV": 1}
    expected_result = {"categories": list(categories.keys())}
    mock_request.get(
        url=f"{settings.server.quiz_api}/categories",
        json=categories,
        status_code=200,
    )
    response = api_client.get("/v1/quizzes/categories")
    assert response.status_code == 200
    result = response.json()
    assert result == expected_result


def test_get_tags(mock_request, settings, api_client):
    tags = ["alcohol", "acting"]
    expected_result = {"tags": tags}
    mock_request.get(
        url=f"{settings.server.quiz_api}/tags",
        json=tags,
        status_code=200,
    )
    response = api_client.get("/v1/quizzes/tags")
    assert response.status_code == 200
    result = response.json()
    assert result == expected_result
