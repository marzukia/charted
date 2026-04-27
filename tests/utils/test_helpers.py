import os
from collections import defaultdict

import pytest

from charted.utils.defaults import BASE_DIR
from charted.utils.helpers import nested_defaultdict, parse_tick_interval


def test_nested_defaultdict():
    nested = nested_defaultdict()
    nested[1][1] = "a"
    assert type(nested) is defaultdict
    assert type(nested[1]) is defaultdict


def test_base_dir():
    from charted.utils.defaults import BASE_DEFINITIONS_DIR

    assert os.path.isdir(BASE_DIR)
    assert os.path.isdir(BASE_DEFINITIONS_DIR)


def test_parse_tick_interval_none():
    assert parse_tick_interval(None) is None


def test_parse_tick_interval_numeric():
    assert parse_tick_interval(5) == 5
    assert parse_tick_interval(10.0) == 10
    assert parse_tick_interval(1) == 1


def test_parse_tick_interval_minimum():
    # intervals < 1 should round up to 1
    assert parse_tick_interval(0.5) == 1
    assert parse_tick_interval(0) == 1
    assert parse_tick_interval(-5) == 1


def test_parse_tick_interval_percentage():
    assert parse_tick_interval("25%", count=100) == 25
    assert parse_tick_interval("10%", count=50) == 5
    assert parse_tick_interval("50%", count=20) == 10


def test_parse_tick_interval_percentage_rounding():
    # 13% of 10 = 1.3, should round down then max to 1
    assert parse_tick_interval("13%", count=10) == 1


def test_parse_tick_interval_percentage_requires_count():
    with pytest.raises(ValueError, match="count is required"):
        parse_tick_interval("25%")


def test_parse_tick_interval_float_proportion():
    # 0.25 as proportion of 100 = 25
    assert parse_tick_interval(0.25, count=100) == 25
    assert parse_tick_interval(0.1, count=50) == 5


def test_parse_tick_interval_float_without_count():
    # 0.25 without count falls through to int(0.25) = 0, then max(1, 0) = 1
    assert parse_tick_interval(0.25) == 1
    assert parse_tick_interval(0.5) == 1
