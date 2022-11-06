def test_cors_header(api_client):
    valid_origin = ["http://localhost:3000", "http://localhost:4200"]
    invalid_origin = ["http://localhost:3200", "http://localhost:4000"]

    valid_responses = [
        api_client.options(
            "/",
            headers={
                "Origin": f"{url}",
            },
        )
        for url in valid_origin
    ]

    for res, url in zip(valid_responses, valid_origin):
        assert res.headers.get("access-control-allow-origin") == url

    invalid_responses = [
        api_client.options(
            "/",
            headers={
                "Origin": f"{url}",
            },
        )
        for url in invalid_origin
    ]

    for res in invalid_responses:
        assert res.headers.get("access-control-allow-origin") is None
