from charted.utils.transform import rotate, translate


def test_rotate():
    x = rotate(180, 50, 50)
    assert x == "rotate(180, 50, 50)"


def test_translate():
    x = translate(-50, 50)
    assert x == "translate(-50, 50)"
