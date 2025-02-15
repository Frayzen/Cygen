import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser, Node

from namespace import NamespaceHolder
from io import open


def parseFile(path) -> NamespaceHolder:

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

    rootNamespace = NamespaceHolder(path, "")

    def parse_cur(node: Node, curNamespace: NamespaceHolder):
        if node.type == "function_declarator":
            curNamespace.push_method(node)
        elif node.type == "namespace_definition":
            return curNamespace.create_subnamespace(node)
        return curNamespace

    def traverse(curNamespace: NamespaceHolder):
        subNamespace = parse_cur(cursor.node, curNamespace)
        if cursor.goto_first_child():
            traverse(subNamespace)
            cursor.goto_parent()
        if cursor.goto_next_sibling():
            traverse(curNamespace)

    traverse(rootNamespace)
    return rootNamespace


defaultPrefix = "#distutils: language = c++\n#cython: language_level = 3\n\n"


def generateCython(namespace: NamespaceHolder, prefix: str = defaultPrefix) -> str:

    def generateNamespace(namespace: NamespaceHolder):
        builder = ""
        if not namespace.empty():
            builder += f'cdef extern from "{namespace.filePath}" namespace "{namespace.name}":\n'
            for m in namespace.methods:
                builder += "    " + str(m) + "\n"
        for sub in namespace.subnamepsaces:
            builder += generateNamespace(sub)
        return builder

    return prefix + generateNamespace(namespace)
