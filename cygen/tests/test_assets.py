from cygen.cygen import generateCython, parseFile
from cygen.context import NamespaceHolder


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
        cppclass InnerClass:
            void defaultPrivate(int a)
    cdef cppclass SubClass:
        SubClass(int* b, char c)
        int other()
    cdef cppclass TestStruct:
        TestStruct(int* a)
        void test(char o)
        cppclass InnerStruct:
            pass
    cdef cppclass SubStruct:
        SubStruct(int* b, char c)
        int other()
    """
    checkGen(namespace, expected)


def test_template():
    namespace = parseFile("tests/assets/templates.hh")
    expected = """
cdef extern from "tests/assets/templates.hh":
    cdef cppclass TestClass[Type]:
        TestClass(Type *a)
        void test(char o)
        OtherType test[OtherType](OtherType a)
        void test[int](int a)
        cppclass InnerClass:
            void defaultPrivate(int a)
    """
    checkGen(namespace, expected)


def test_typedef():
    namespace = parseFile("tests/assets/typedef.hh")
    expected = """
cdef extern from "tests/assets/typedef.hh":
    cdef cppclass Ok:
        pass
    Ok test(Ok a, Ok* b)
    """
    checkGen(namespace, expected)
