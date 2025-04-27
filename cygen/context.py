from tree_sitter import Node
from typing import List
import re


def process_type(v: str):
    v = v.replace("<", "[").replace(">", "]")
    v = v.replace("std::", "")
    v = re.sub("enum \\w+", "int", v) # handle enums
    return v


class Method:
    def __init__(self, retType: str, name: str, params: str) -> None:
        self.retType = retType
        self.name = name
        self.params = params

    def __str__(self) -> str:
        s = ""
        if self.retType != "":
            s = self.retType + " "
        return s + self.name + self.params


class ContextHolder:
    def __init__(self, parent) -> None:
        self.parent_namespace = parent
        self.methods: List[Method] = []
        self.classes: List[ClassHolder] = []
        self.sys_includes: List[str] = []
        self.local_includes: List[str] = []
        self.typenames: List[str] = []
        self.template = None

    def empty(self):  # if it is worth printing
        return len(self.methods) == 0 and len(self.classes) == 0

    def push_method(self, node: Node) -> None:
        retTypeNode = node.parent.child_by_field_name("type")
        methodName = node.child_by_field_name("declarator").text.decode()
        if self.template is not None:
            methodName += f"[{self.template}]"
            self.template = None
        parameters = node.child_by_field_name("parameters").text.decode()
        retType = (
                    process_type(retTypeNode.text.decode())
                    if retTypeNode is not None
                    else ""
                )
        self.methods.append(
            Method(
                retType,
                methodName,
                process_type(parameters),
            )
        )

    def push_typename(self, node: Node) -> None:
        self.typenames.append(node.child_by_field_name("declarator").text.decode())

    def push_include(self, node: Node) -> None:
        nodetxt = node.child_by_field_name("path").text.decode()
        if nodetxt[0] == "<":
            self.sys_includes.append(nodetxt[1:-1])
        else:
            self.local_includes.append(nodetxt[1:-1])

    def create_subclass(self, node: Node):
        className = node.child_by_field_name("name").text.decode()
        if self.template is not None:
            className += f"[{self.template}]"
            self.template = None
        isStruct = node.type == "struct_specifier"
        subclass = ClassHolder(self, className, not isStruct)
        self.classes.append(subclass)
        return subclass

    def set_template(self, node: Node):
        params = node.child_by_field_name("parameters")
        if len(params.children) != 3:
            raise Exception(
                f"The template {node.text} should not have more than 1 template argument"
            )
        first = params.children[1].children[0].text.decode()
        second = params.children[1].children[1].text.decode()
        if first == "typename":
            self.template = second
        else:
            self.template = first


class ClassHolder(ContextHolder):
    def __init__(self, parent: ContextHolder, name: str, public_access: bool) -> None:
        self.name = name
        self.public_access = public_access
        super().__init__(parent)

    def set_access(self, node: Node):
        self.public_access = node.text.decode() == "public"

    def push_method(self, node: Node) -> None:
        if self.public_access:
            super().push_method(node)


class NamespaceHolder(ContextHolder):
    def __init__(self, parent: ContextHolder, filePath: str, name: str) -> None:
        self.filePath = filePath
        self.name = name
        self.subnamespaces: List[NamespaceHolder] = []
        super().__init__(parent)

    def create_subnamespace(self, node: Node):
        name = node.child_by_field_name("name").text.decode()
        sub = NamespaceHolder(
            self,
            self.filePath,
            self.name + "::" + name if self.name != "" else name,
        )
        self.subnamespaces.append(sub)
        return sub
