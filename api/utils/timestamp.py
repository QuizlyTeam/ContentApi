from time import time


def get_timestamp() -> str:
    """
    Get the current timestamp.
    :return: the timestamp
    """
    return str(int(time()))
