# node.py

class Node:
    def __init__(self, label: str, group: str = "intermediate"):
        self.label = label
        self.group = group
        self.children = []
        self.properties = {}

    def add_child(self, child: 'Node', value: float):
        self.children.append((child, value))

def collect_nodes(root: Node):
    priority = {
        "income": -20,
        "savings": 0,
        "intermediate": 10,
        "holding": 15,
        "expense": 20,
        "unallocated": 25
    }
    nodes = []
    visited = set()

    def recurse(node):
        if id(node) in visited:
            return
        visited.add(id(node))
        nodes.append(node)
        sorted_children = sorted(
            node.children,
            key=lambda item: priority.get(item[0].group, 30)
        )
        for child, _ in sorted_children:
            recurse(child)
    if root:
        recurse(root)
    return nodes