from collections import defaultdict
import os


def nested_defaultdict() -> defaultdict:
    return defaultdict(nested_defaultdict)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
