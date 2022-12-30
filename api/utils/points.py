def points_function(t: float) -> float:
    """
    Return points equivalent to time spend on answer.

    :param t: Time spend on answer.
    :return: Points.
    """
    return round(
        8.31828329 * 1.2 ** (-(t - 12.23262668)) / 0.13756839 - 62.72982658
    )
