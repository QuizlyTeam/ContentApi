def test_parse_url(parse_url):
    """
    Test the parse_url function.
    """
    """"""
    url = 'http://127.0.0.1:8000'
    options = {
        'a': 5
    }
    assert parse_url(url, options) == url + '?a=5'

