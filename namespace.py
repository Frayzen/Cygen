from tree_sitter import Node
from typing import List


class Method:
    def __init__(self, retType: str, name: str, params: str) -> None:
        self.retType = retType
        self.name = name
        self.params = params

    def __str__(self) -> str:
        return self.retType + " " + self.name + " " + self.params


class NamespaceHolder:
    def __init__(self, filePath: str, name: str) -> None:
        self.filePath = filePath
        self.name = name
        self.methods: List[Method] = []
        self.subnamepsaces: List[NamespaceHolder] = []
        self.classes = []

    def empty(self):  # if it is worth printing
        return len(self.methods) == 0 and len(self.classes) == 0

    def push_method(self, node: Node) -> None:
        self.methods.append(
            Method(
                node.parent.child_by_field_name("type").text.decode(),
                node.child_by_field_name("declarator").text.decode(),
                node.child_by_field_name("parameters").text.decode(),
            )
        )

    def create_subnamespace(self, node: Node):
        sub = NamespaceHolder(
            self.filePath,
            self.name + "::" + node.child_by_field_name("name").text.decode(),
        )
        self.subnamepsaces.append(sub)
        return sub

    def __str__(self) -> str:
        s = f"NAMESPACE '{self.name}' ({len(self.methods)}) methods:\n"
        for m in self.methods:
            s += "    " + str(m) + "\n"

        return s
