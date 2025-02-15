import tree_sitter_cpp as tscpp
from tree_sitter import Language, Parser, Node

from context import ClassHolder, ContextHolder, NamespaceHolder
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

    def parse_cur(node: Node, context: ContextHolder):
        if node.type == "function_declarator":
            context.push_method(node)
        elif node.type == "namespace_definition" and isinstance(
            context, NamespaceHolder
        ):
            return context.create_subnamespace(node)
        elif node.type == "class_specifier" or node.type == "struct_specifier":
            return context.create_subclass(node)
        elif node.type == "access_specifier":
            assert isinstance(context, ClassHolder)
            context.set_access(node)
        return context

    def traverse(curContext: ContextHolder):
        subContext = parse_cur(cursor.node, curContext)
        if cursor.goto_first_child():
            traverse(subContext)
            cursor.goto_parent()
        if cursor.goto_next_sibling():
            traverse(curContext)

    traverse(rootNamespace)
    return rootNamespace


defaultPrefix = "#distutils: language = c++\n#cython: language_level = 3\n\n"


def generateCython(namespace: NamespaceHolder, prefix: str = defaultPrefix) -> str:

    def generateContext(context: ContextHolder, tabs=""):
        builder = ""
        if isinstance(context, ClassHolder):
            builder += f"{tabs}cdef cppclass {context.name}:\n"
        for m in context.methods:
            builder += tabs + "    " + str(m) + "\n"
        for subc in context.classes:
            builder += generateContext(subc, tabs="    " + tabs)
        return builder

    def generateNamespace(namespace: ContextHolder):
        builder = ""
        if not namespace.empty():
            namespacedef = (
                "" if namespace.name == "" else f' namespace "{namespace.name}"'
            )
            builder += f'cdef extern from "{namespace.filePath}"{namespacedef}:\n'
            builder += generateContext(namespace)
        for sub in namespace.subnamespaces:
            builder += generateNamespace(sub)
        return builder

    return prefix + generateNamespace(namespace)
