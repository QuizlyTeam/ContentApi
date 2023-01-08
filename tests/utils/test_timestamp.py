def test_get_timestamp(mocker, get_timestamp):
    """
    Test the get_timestamp function.
    """
    mocker.patch("api.utils.timestamp.time", return_value=420.125111234)

    assert get_timestamp() == "420"
