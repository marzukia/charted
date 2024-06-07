from collections import defaultdict
import os
from charted.utils.helpers import BASE_DIR, nested_defaultdict


def test_nested_defaultdict():
    nested = nested_defaultdict()
    nested[1][1] = "a"
    assert type(nested) is defaultdict
    assert type(nested[1]) is defaultdict


def test_base_dir():
    current_dir = os.getcwd()
    assert BASE_DIR == current_dir
