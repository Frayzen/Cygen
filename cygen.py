import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser, Node

from namespace import NamespaceHolder
from io import open


def parseFile(path):

    # Compile the C++ grammar
    fileContent = open(path).read()
    CPP_LANGUAGE = Language(tscpp.language())
    parser = Parser(CPP_LANGUAGE)
    parser.language = CPP_LANGUAGE
    tree = parser.parse(
        bytes(
            fileContent,
            "utf8",
        )
    )
    cursor = tree.walk()

    namespace = NamespaceHolder("")

    def parse_cur(node: Node):
        if node.type == "function_declarator":
            namespace.push_method(node)

    def traverse():
        if cursor.goto_first_child():
            traverse()
            cursor.goto_parent()
        parse_cur(cursor.node)
        if cursor.goto_next_sibling():
            traverse()

    traverse()
    return namespace
