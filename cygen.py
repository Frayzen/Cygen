from enum import Enum
from os import makedirs
import os
from os.path import dirname
import tree_sitter_cpp as tscpp
from includes import include_almanac
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

    rootNamespace = NamespaceHolder(None, path, "")

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
        elif node.type == "template_declaration":
            context.set_template(node)
        elif node.type == "type_definition":
            context.push_typename(node)
        elif node.type == "preproc_include":
            context.push_include(node)
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

    def generateContext(context: ContextHolder, depth=0):
        builder = ""
        tabs = depth * "    "
        for typename in context.typenames:
            builder += f"    {tabs}cdef cppclass {typename}:\n        {tabs}pass\n"
        for m in context.methods:
            builder += tabs + "    " + str(m) + "\n"
        for subc in context.classes:
            builder += generateContext(subc, depth=depth + 1)
        if builder == "":
            builder = f"{tabs}    pass\n"
        if isinstance(context, ClassHolder):
            classheader = f"{tabs}"
            if isinstance(context.parent_namespace, NamespaceHolder):
                classheader += "cdef "
            classheader += f"cppclass {context.name}:\n"
            builder = classheader + builder
        return builder

    def generateNamespace(namespace: ContextHolder):
        builder = ""
        for include in namespace.sys_includes:
            if include in include_almanac:
                builder += f"from libcpp cimport {include}\n"
        for include in namespace.local_includes:
            package = ".".join(include.split("/"))
            package = ".".join(package.split(".")[:-1])
            builder += f"from {package} cimport *"

        builder += "\n"
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


if __name__ == "__main__":
    import argparse

    ap = argparse.ArgumentParser(
        "cygen", "cygen [-o directory] [-p] [-v|-vv] [-s] files..."
    )
    ap.add_argument("-o", "--out", default="./", help="The output folder")
    ap.add_argument("-p", "--prefix", help="The cython prefix on each generated file")
    ap.add_argument("-v", "-vv", "--verbose", action="count", default=0)
    ap.add_argument("files", nargs="+")
    res = ap.parse_args()

    prefix = defaultPrefix if res.prefix is None else res.prefix

    makedirs(res.out, exist_ok=True)

    absolute_paths = [os.path.abspath(path) for path in res.files]
    common_parent = os.path.commonpath(absolute_paths)
    out_relative_paths = [
        os.path.relpath(".".join(path.split(".")[:-1]) + ".pxd", common_parent)
        for path in res.files
    ]

    for i in range(len(res.files)):
        inpath = absolute_paths[i]
        relpath = out_relative_paths[i]
        outpath = os.path.abspath(res.out + os.sep + relpath)
        if res.verbose >= 1:
            print(f"{outpath}", flush=True)
        if res.verbose >= 2:
            print(f"Generating {outpath} from {inpath}...", flush=True)
        namespace = parseFile(inpath)
        generated = generateCython(namespace)
        makedirs(dirname(outpath), exist_ok=True)
        with open(outpath, mode="w") as out:
            out.write(generated)
            out.close()
