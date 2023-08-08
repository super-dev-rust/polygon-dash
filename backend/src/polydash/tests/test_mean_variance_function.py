import pytest

from polydash.rating.live_time_transaction import calculate_mean_variance


@pytest.fixture
def mean_variance_test_fixture():
    pass


def test_mean_variance_calculation(mean_variance_test_fixture):
    mean, variance, counted, too_low, too_big = calculate_mean_variance(1, 0, 0, 0)
    assert mean == 1
    assert variance == 0
    assert counted == 1
    assert not too_low
    assert not too_big

    mean, variance, counted, too_low, too_big = calculate_mean_variance(
        2, mean, variance, counted
    )
    assert round(mean, 2) == 1.5
    assert round(variance, 2) == 0.25
    assert counted == 2
    assert not too_low
    assert not too_big

    mean, variance, counted, too_low, too_big = calculate_mean_variance(
        3, mean, variance, counted
    )
    assert round(mean, 2) == 2
    assert round(variance, 2) == 0.67
    assert counted == 3
    assert not too_low
    assert not too_big

    mean, variance, counted, too_low, too_big = calculate_mean_variance(
        10, mean, variance, counted
    )
    assert round(mean, 2) == 4
    assert round(variance, 2) == 12.5
    assert counted == 4
    assert not too_low
    assert too_big

    mean, variance, counted, too_low, too_big = calculate_mean_variance(
        -10, mean, variance, counted
    )
    assert round(mean, 2) == 1.2
    assert round(variance, 2) == 41.36
    assert counted == 5
    assert too_low
    assert not too_big
