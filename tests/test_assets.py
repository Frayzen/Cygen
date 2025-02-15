from cygen import generateCython, parseFile
from namespace import NamespaceHolder


def checkGen(namespace: NamespaceHolder, expected: str):
    def cleanup(s: str) -> str:
        return s.replace(" ", "").replace("\n", "")

    generated = generateCython(namespace, "")
    print(generated)
    if cleanup(generated) != cleanup(expected):
        print("DIFFERENCE /!\\")
        print("GOT\n\n", generated, "\n\n EXPECTED \n\n", expected)
        assert False


def test_basic():
    namespace = parseFile("tests/assets/basic.hh")
    expected = """
 cdef extern from "tests/assets/basic.hh" namespace "":
    int add (int a, int b)
    int pow (float a, int& b)
"""
    checkGen(namespace, expected)


def test_namespace():
    namespace = parseFile("tests/assets/namespaces.hh")
    expected = """
cdef extern from "tests/assets/namespaces.hh" namespace "::First":
    int first_method (int a)
cdef extern from "tests/assets/namespaces.hh" namespace "::First::Second":
    int second_method (int a, int b)
"""
    checkGen(namespace, expected)
