from cygen import parseFile


def test_basic():
    namespace = parseFile("tests/assets/basic.hh")
    assert len(namespace.methods) == 2
