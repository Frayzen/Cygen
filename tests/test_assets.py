from cygen import generateCython, parseFile
from context import NamespaceHolder


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
 cdef extern from "tests/assets/basic.hh":
    int add (int a, int b)
    int pow (float a, int& b)
"""
    checkGen(namespace, expected)


def test_namespace():
    namespace = parseFile("tests/assets/namespaces.hh")
    expected = """
cdef extern from "tests/assets/namespaces.hh" namespace "First":
    int first_method (int a)
cdef extern from "tests/assets/namespaces.hh" namespace "First::Second":
    int second_method (int a, int b)
"""
    checkGen(namespace, expected)


def test_classes():
    namespace = parseFile("tests/assets/classes.hh")
    expected = """
cdef extern from "tests/assets/classes.hh":
    cdef cppclass TestClass:
        TestClass(int* a)
        void test(char o)
        cdef cppclass InnerClass:
            void defaultPrivate(int a)
    cdef cppclass SubClass:
        SubClass(int* b, char c)
        int other()
    cdef cppclass TestStruct:
        TestStruct(int* a)
        void test(char o)
        cdef cppclass InnerStruct:
    cdef cppclass SubStruct:
        SubStruct(int* b, char c)
        int other()
    """
    checkGen(namespace, expected)
