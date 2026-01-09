# node.py

from typing import List


class Node:
    """Core data structure for budget nodes."""
    def __init__(self, label: str, group: str = "intermediate"):
        self.label = label
        self.group = group
        self.children: List[tuple['Node', float]] = []  # (child_node, flow_value)
        self.properties: dict = {}  # e.g., {"apr": 5.0, "current_balance": 0.0} for savings

    def add_child(self, child: 'Node', value: float):
        self.children.append((child, value))