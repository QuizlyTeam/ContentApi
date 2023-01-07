def parse_url(url: str, options: dict) -> str:
    """
    Parse the url and add the options to it.
    :param url: - the url to parse
    :param options: - the options to add to the url
    :return: the parsed url
    """
    _url = url + "?"
    for key, value in options.items():
        if value is not None:
            if isinstance(value, list):
                _url += key + "=" + ",".join(value)
            else:
                _url += key + "=" + str(value)
            _url += "&"

    return _url[:-1]
