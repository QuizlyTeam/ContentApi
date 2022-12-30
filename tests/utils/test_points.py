def test_points_0(points_function):
    """Points function should return 500 points when time = 0 seconds"""
    assert points_function(0) == 500


def test_points_between_0_and_12(points_function):
    """Points function should return points between 0 and 500 when time is between 0 and 12"""
    assert points_function(6) > 0
    assert points_function(6) < 500


def test_points_12(points_function):
    """Points function should return 0 points when time = 12 seconds"""
    assert points_function(12) == 0
