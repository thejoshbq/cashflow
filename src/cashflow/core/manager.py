# manager.py

from typing import Optional, List, Dict
from collections import defaultdict
import plotly.graph_objects as go
from ..models.node import Node


def collect_nodes(root: Optional[Node]) -> List[Node]:
    """DFS traversal with priority sorting for visual grouping."""
    if not root:
        return []
    priority = {
        "income": -20,
        "savings": 0,
        "intermediate": 10,
        "holding": 15,
        "expense": 20,
        "unallocated": 25
    }
    nodes: List[Node] = []
    visited = set()

    def recurse(node: Node):
        node_id = id(node)
        if node_id in visited:
            return
        visited.add(node_id)
        nodes.append(node)
        sorted_children = sorted(
            node.children,
            key=lambda item: priority.get(item[0].group, 30)
        )
        for child, _ in sorted_children:
            recurse(child)

    recurse(root)
    return nodes

class BudgetManager:
    """Manages the entire budget state and generates visualization data."""
    def __init__(self):
        self.planned_income: float = 0.0
        self.root: Optional[Node] = None
        self.nodes: Dict[str, Node] = {}
        self.assets: List[Dict[str, float]] = []

    def start(self, income: float):
        if income <= 0:
            raise ValueError("Income must be positive")
        self.root = Node("Income", "income")
        self.nodes = {"Income": self.root}
        self.planned_income = income

    def edit_income(self, income: float):
        if income <= 0:
            raise ValueError("Income must be positive")
        self.planned_income = income

    def add_node(self, parent_label: str, label: str, amount: float, group: str,
                 apr: float = 0.0, current_balance: float = 0.0):
        if label in self.nodes:
            raise ValueError("Node name already exists")
        if amount <= 0:
            raise ValueError("Amount must be positive")
        if parent_label not in self.nodes:
            raise ValueError("Parent not found")
        parent = self.nodes[parent_label]
        new_node = Node(label, group)
        parent.add_child(new_node, amount)
        self.nodes[label] = new_node
        if group == "savings":
            new_node.properties["apr"] = apr
            new_node.properties["current_balance"] = current_balance

    def edit_node(self, label: str, new_label: Optional[str] = None,
                  new_amount: Optional[float] = None, new_group: Optional[str] = None,
                  apr: Optional[float] = None, current_balance: Optional[float] = None):
        if label not in self.nodes:
            raise ValueError("Node not found")
        if label == "Income":
            raise ValueError("Cannot edit root Income node directly")
        node = self.nodes[label]
        parent = self.find_parent(node)
        if not parent:
            raise ValueError("Parent not found")

        if new_amount is not None:
            if new_amount <= 0:
                raise ValueError("Amount must be positive")
            for i, (child, val) in enumerate(parent.children):
                if child is node:
                    parent.children[i] = (child, new_amount)
                    break

        if new_label and new_label != label:
            if new_label in self.nodes:
                raise ValueError("New name already exists")
            node.label = new_label
            del self.nodes[label]
            self.nodes[new_label] = node

        if new_group:
            node.group = new_group
            if new_group != "savings":
                node.properties.clear()

        if node.group == "savings":
            if apr is not None:
                node.properties["apr"] = apr
            if current_balance is not None:
                node.properties["current_balance"] = current_balance

    def remove_node(self, label: str):
        if label not in self.nodes:
            raise ValueError("Node not found")
        if label == "Income":
            raise ValueError("Cannot remove root")
        node = self.nodes[label]
        parent = self.find_parent(node)
        if parent:
            parent.children = [c for c in parent.children if c[0] is not node]
        to_remove = []
        def collect(n: Node):
            to_remove.append(n.label)
            for c, _ in n.children:
                collect(c)
        collect(node)
        for l in to_remove:
            del self.nodes[l]

    def find_parent(self, child: Node) -> Optional[Node]:
        for p in self.nodes.values():
            if any(c[0] is child for c in p.children):
                return p
        return None

    def check_over_allocations(self) -> List[str]:
        if not self.root:
            return []
        over = []
        total_allocated = sum(val for _, val in self.root.children)
        if total_allocated > self.planned_income + 0.01:
            over.append("Overall budget")
        inflow = {self.root: self.planned_income}
        def recurse(node: Node):
            node_in = inflow[node]
            node_out = sum(val for _, val in node.children)
            if node_out > node_in + 0.01:
                over.append(node.label)
            for child, val in node.children:
                inflow[child] = val
                recurse(child)
        recurse(self.root)
        return over

    def get_visualization_data(self, projection_months: int = 0) -> Dict:
        if not self.root:
            raise ValueError("Budget not started")

        all_nodes = collect_nodes(self.root)
        node_index = {node: i for i, node in enumerate(all_nodes)}

        inflow = {node: 0.0 for node in all_nodes}
        for node in all_nodes:
            for child, val in node.children:
                inflow[child] += val

        allocated = sum(val for _, val in self.root.children)
        virtual_node = None
        if self.planned_income - allocated > 0.01:
            surplus = self.planned_income - allocated
            virtual_node = Node("Unallocated Surplus", "unallocated")
            self.root.children.append((virtual_node, surplus))

        all_nodes = collect_nodes(self.root)
        node_index = {node: i for i, node in enumerate(all_nodes)}
        if virtual_node:
            self.root.children.pop()

        display_value = {}
        for node in all_nodes:
            outflow = sum(val for _, val in node.children)
            display_value[node] = outflow if outflow > 0 else inflow.get(node, 0)

        labels = []
        for n in all_nodes:
            if n is self.root:
                labels.append(f"Income<br>Planned: ${self.planned_income:,.0f}<br>Allocated: ${allocated:,.0f}")
            else:
                labels.append(f"{n.label}<br>${display_value[n]:,.0f}")

        over_set = set(self.check_over_allocations())
        node_colors = []
        for n in all_nodes:
            if n.label in over_set:
                node_colors.append("#FF0000")
            elif n.group == "income":
                node_colors.append("#90EE90")
            elif n.group == "savings":
                node_colors.append("#228B22")
            elif n.group == "expense":
                node_colors.append("#FF6347")
            elif n.group == "holding":
                node_colors.append("#4682B4")
            elif n.group == "unallocated":
                node_colors.append("#FFA500")
            else:
                node_colors.append("#A9A9A9")

        sources, targets, values, link_colors = [], [], [], []
        for node in all_nodes:
            for child, val in node.children:
                sources.append(node_index[node])
                targets.append(node_index[child])
                values.append(val)
                cg = child.group
                if cg == "savings":
                    link_colors.append("rgba(34, 139, 34, 0.6)")
                elif cg == "expense":
                    link_colors.append("rgba(255, 99, 71, 0.6)")
                elif cg == "unallocated":
                    link_colors.append("rgba(255, 165, 0, 0.6)")
                else:
                    link_colors.append("rgba(70, 130, 180, 0.6)")

        sankey_fig = go.Figure(go.Sankey(
            arrangement="snap",
            node=dict(pad=30, thickness=40, line=dict(color="black", width=1), label=labels, color=node_colors),
            link=dict(source=sources, target=targets, value=values, color=link_colors)
        ))
        sankey_fig.update_layout(title_text="Monthly Cash Flow", font_size=13, height=600)

        category_totals = defaultdict(float)
        def cat_recurse(node: Node):
            for child, val in node.children:
                if not child.children:
                    category_totals[child.group] += val
                cat_recurse(child)
        cat_recurse(self.root)
        expense_total = category_totals["expense"]
        percent = (expense_total / self.planned_income * 100) if self.planned_income > 0 else 0
        gauge_color = "red" if percent > 100 else "darkorange" if percent > 80 else "green"
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=percent,
            number={"suffix": "%"},
            title={"text": "Expenses as % of Income"},
            gauge={
                "axis": {"range": [None, 130]},
                "bar": {"color": gauge_color},
                "steps": [{"range": [0, 80], "color": "lightgreen"}, {"range": [80, 100], "color": "yellow"}, {"range": [100, 130], "color": "red"}]
            }
        ))
        gauge_fig.update_layout(height=300)

        if not self.assets:
            pie_labels = ["No assets yet"]
            pie_values = [1]
        else:
            pie_labels = [a["name"] for a in self.assets]
            pie_values = [a["value"] for a in self.assets]
        pie_fig = go.Figure(go.Pie(labels=pie_labels, values=pie_values, hole=0.4,
                                   textinfo="label+value+percent" if self.assets else "label"))
        pie_fig.update_layout(title_text="Standalone Assets", height=400)

        projection = None
        if projection_months > 0:
            accumulating = [n for n in all_nodes if not n.children and n.group == "savings"]
            if accumulating:
                time_points = list(range(projection_months + 1))
                total_proj = [0] * (projection_months + 1)
                traces = []
                for node in accumulating:
                    contrib = inflow.get(node, 0)
                    current = node.properties.get("current_balance", 0.0)
                    apr = node.properties.get("apr", 0.0) / 100 / 12
                    bal = current
                    balances = [round(bal, 2)]
                    for _ in range(projection_months):
                        bal = bal * (1 + apr) + contrib
                        balances.append(round(bal, 2))
                    total_proj = [a + b for a, b in zip(total_proj, balances)]
                    traces.append({"type": "scatter", "x": time_points, "y": balances,
                                   "mode": "lines+markers", "name": f"{node.label} Projected"})
                traces.append({"type": "scatter", "x": time_points, "y": total_proj,
                               "mode": "lines+markers", "name": "Total Savings Projected",
                               "line": {"width": 5, "dash": "dot"}})
                projection = {"data": traces, "layout": {"xaxis": {"title": "Months"},
                                                        "yaxis": {"title": "Balance ($)"}, "height": 500}}

        unalloc = self.planned_income - allocated
        summary = f"<b>Budget Summary</b><br><br>Planned Income: <b>${self.planned_income:,.0f}</b><br>Total Allocated: <b>${allocated:,.0f}</b><br><br>"
        if unalloc > 0:
            summary += f"Surplus: <span style='color:#228B22;'>${unalloc:,.0f}</span><br>"
        elif unalloc < 0:
            summary += f"Deficit: <span style='color:red;'>${-unalloc:,.0f}</span><br>"
        summary += f"Savings/Investments: <b>${category_totals['savings']:,.0f}</b><br>Expenses: <b>${expense_total:,.0f}</b><br><br>"
        assets_total = sum(a["value"] for a in self.assets)
        summary += f"Standalone Assets Total: <b>${assets_total:,.0f}</b>"

        over = self.check_over_allocations()
        warning = f"⚠ Over-allocation detected in: {', '.join(over)}" if over else ""

        return {
            "sankey": sankey_fig.to_dict(),
            "gauge": gauge_fig.to_dict(),
            "pie": pie_fig.to_dict(),
            "projection": projection,
            "summary": summary,
            "warning": warning
        }

manager = BudgetManager()