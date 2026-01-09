import sys
from collections import defaultdict

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, QWidget, QPushButton,
    QLabel, QListWidget, QMessageBox, QDialog, QFormLayout,
    QComboBox, QLineEdit, QDialogButtonBox, QSplitter, QInputDialog, QSpinBox
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtGui import QDoubleValidator
from PySide6.QtCore import Qt

import plotly.graph_objects as go
from plotly.subplots import make_subplots


class Node:
    """Node with optional properties for savings (APR, current balance)."""
    def __init__(self, label: str, group: str = "intermediate"):
        self.label = label
        self.group = group
        self.children = []  # list of (child_node, flow_value)
        self.properties = {}  # e.g., {"apr": 5.0, "current_balance": 0.0} for savings


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


class NodeDialog(QDialog):
    """Unified dialog for adding or editing nodes with dynamic savings fields."""
    def __init__(self, parent=None, current_labels=None, edit_node=None):
        super().__init__(parent)
        self.edit_node = edit_node
        self.old_label = edit_node.label if edit_node else None
        self.setWindowTitle("Edit Node" if edit_node else "Add New Node")

        layout = QFormLayout(self)

        # Parent (disabled for edit)
        self.parent_combo = QComboBox()
        if current_labels:
            self.parent_combo.addItems(sorted(current_labels))
        self.parent_combo.setEnabled(edit_node is None)
        if edit_node:
            parent = self.find_parent(edit_node)
            if parent:
                self.parent_combo.setCurrentText(parent.label)
        layout.addRow("Parent Node:", self.parent_combo)

        # Name
        self.name_edit = QLineEdit()
        if edit_node:
            self.name_edit.setText(edit_node.label)
        layout.addRow("Node Name:", self.name_edit)

        # Amount
        self.amount_edit = QLineEdit()
        self.amount_edit.setValidator(QDoubleValidator(0.01, 10000000.0, 2))
        if edit_node and edit_node is not self.parent().root:  # can't edit root "amount"
            parent_node = self.find_parent(edit_node)
            if parent_node:
                for child, val in parent_node.children:
                    if child is edit_node:
                        self.amount_edit.setText(str(val))
                        break
        layout.addRow("Monthly Flow Amount:", self.amount_edit)

        # Group/Type
        self.group_combo = QComboBox()
        self.group_combo.addItems(["intermediate", "savings", "expense", "holding"])
        if edit_node:
            self.group_combo.setCurrentText(edit_node.group)
        layout.addRow("Node Type (color):", self.group_combo)

        # Savings extras
        self.apr_label = QLabel("Annual Interest Rate (%):")
        self.apr_edit = QLineEdit()
        self.apr_edit.setValidator(QDoubleValidator(0.0, 20.0, 2))
        layout.addRow(self.apr_label, self.apr_edit)

        self.balance_label = QLabel("Current Balance ($):")
        self.balance_edit = QLineEdit()
        self.balance_edit.setValidator(QDoubleValidator(0.0, 1000000000.0, 2))
        layout.addRow(self.balance_label, self.balance_edit)

        # Initial visibility & values
        self.toggle_savings_fields(self.group_combo.currentText())
        self.group_combo.currentTextChanged.connect(self.toggle_savings_fields)

        if edit_node and edit_node.group == "savings":
            self.apr_edit.setText(str(edit_node.properties.get("apr", 0.0)))
            self.balance_edit.setText(str(edit_node.properties.get("current_balance", 0.0)))

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def toggle_savings_fields(self, group):
        visible = group == "savings"
        self.apr_label.setVisible(visible)
        self.apr_edit.setVisible(visible)
        self.balance_label.setVisible(visible)
        self.balance_edit.setVisible(visible)
        if visible and self.apr_edit.text() == "":
            self.apr_edit.setText("0.0")
            self.balance_edit.setText("0.0")

    def find_parent(self, child):
        return self.parent().find_parent_node(child) if self.parent() else None


class AddAssetDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Add Standalone Asset")
        layout = QFormLayout(self)

        self.name_edit = QLineEdit()
        layout.addRow("Asset Name:", self.name_edit)

        self.amount_edit = QLineEdit()
        self.amount_edit.setValidator(QDoubleValidator(0.0, 1000000000.0, 2))
        layout.addRow("Current Value ($):", self.amount_edit)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Interactive Budget Cashflow Sankey Diagram")
        self.resize(1800, 1200)

        central = QWidget()
        main_layout = QVBoxLayout(central)

        instructions = QLabel(
            "<h3>Interactive Budget Visualization</h3>"
            "• Click <b>Start</b> → enter planned monthly income → creates only 'Income' node.<br>"
            "• Use <b>Edit Planned Income</b> (after starting) to change the planned monthly income amount.<br>"
            "• <b>Add Node</b>: allocate from any parent (savings nodes ask for APR & current balance).<br>"
            "• <b>Edit Selected</b>: change name, amount, type, or savings details (root 'Income' cannot be edited directly).<br>"
            "• Over-allocations show red warning + highlighted nodes.<br>"
            "• Gauge shows expense % of income.<br>"
            "• Set projection months → line chart of savings growth."
        )
        instructions.setWordWrap(True)
        main_layout.addWidget(instructions)

        self.start_btn = QPushButton("Start Building Your Budget")
        self.start_btn.setStyleSheet("font-size: 24px; padding: 20px; background: #4CAF50; color: white;")
        self.start_btn.clicked.connect(self.start_budget)
        main_layout.addWidget(self.start_btn, alignment=Qt.AlignCenter)

        self.splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(self.splitter, stretch=1)

        # Left controls
        controls = QWidget()
        controls_layout = QVBoxLayout(controls)

        controls_layout.addWidget(QLabel("<b>Cashflow Nodes:</b>"))
        self.node_list = QListWidget()
        controls_layout.addWidget(self.node_list)

        node_btns = QHBoxLayout()
        self.add_btn = QPushButton("Add Node")
        self.add_btn.clicked.connect(self.show_add_dialog)
        self.add_btn.setEnabled(False)
        self.edit_btn = QPushButton("Edit Selected")
        self.edit_btn.clicked.connect(self.show_edit_dialog)
        self.edit_btn.setEnabled(False)
        self.remove_btn = QPushButton("Remove Selected")
        self.remove_btn.clicked.connect(self.remove_selected_node)
        self.remove_btn.setEnabled(False)
        self.edit_income_btn = QPushButton("Edit Planned Income")
        self.edit_income_btn.clicked.connect(self.edit_planned_income)
        self.edit_income_btn.setEnabled(False)
        node_btns.addWidget(self.add_btn)
        node_btns.addWidget(self.edit_btn)
        node_btns.addWidget(self.remove_btn)
        node_btns.addWidget(self.edit_income_btn)
        controls_layout.addLayout(node_btns)

        controls_layout.addWidget(QLabel("<b>Budget Summary:</b>"))
        self.summary_label = QLabel()
        self.summary_label.setWordWrap(True)
        # Removed explicit light background for better dark mode compatibility
        self.summary_label.setStyleSheet("padding: 10px; border: 1px solid #aaa;")
        self.summary_label.setMinimumHeight(150)
        controls_layout.addWidget(self.summary_label)

        self.warning_label = QLabel()
        self.warning_label.setStyleSheet("color: #FF0000; font-weight: bold; padding: 8px;")
        self.warning_label.setWordWrap(True)
        controls_layout.addWidget(self.warning_label)

        controls_layout.addWidget(QLabel("<b>Projection horizon (months):</b>"))
        self.projection_spin = QSpinBox()
        self.projection_spin.setRange(0, 240)
        self.projection_spin.setValue(0)
        self.projection_spin.valueChanged.connect(self.update_diagram)
        self.projection_spin.setEnabled(False)
        controls_layout.addWidget(self.projection_spin)

        controls_layout.addWidget(QLabel("<b>Standalone Assets:</b>"))
        self.asset_list = QListWidget()
        controls_layout.addWidget(self.asset_list)

        asset_btns = QHBoxLayout()
        self.add_asset_btn = QPushButton("Add Asset")
        self.add_asset_btn.clicked.connect(self.show_add_asset_dialog)
        self.remove_asset_btn = QPushButton("Remove Selected")
        self.remove_asset_btn.clicked.connect(self.remove_selected_asset)
        asset_btns.addWidget(self.add_asset_btn)
        asset_btns.addWidget(self.remove_asset_btn)
        controls_layout.addLayout(asset_btns)

        controls_layout.addStretch()
        self.splitter.addWidget(controls)

        # Right diagram
        self.view = QWebEngineView()
        self.splitter.addWidget(self.view)
        self.splitter.setSizes([500, 1300])

        self.setCentralWidget(central)

        # Data
        self.started = False
        self.planned_income = 0.0
        self.root = None
        self.nodes = {}
        self.assets = []

        self.update_diagram()

    def find_parent_node(self, child):
        for p in self.nodes.values():
            if any(c[0] is child for c in p.children):
                return p
        return None

    def start_budget(self):
        amount, ok = QInputDialog.getDouble(
            self,
            "Planned Monthly Income",
            "Enter your planned total monthly income:",
            10000.0,
            0.01,
            10000000.0,
            2
        )
        if not ok or amount <= 0:
            return

        self.root = Node("Income", "income")
        self.nodes = {"Income": self.root}
        self.planned_income = amount

        self.started = True
        self.start_btn.setVisible(False)
        self.add_btn.setEnabled(True)
        self.edit_btn.setEnabled(True)
        self.remove_btn.setEnabled(True)
        self.edit_income_btn.setEnabled(True)
        self.projection_spin.setEnabled(True)

        self.update_node_list()
        self.update_asset_list()
        self.update_diagram()

    def edit_planned_income(self):
        amount, ok = QInputDialog.getDouble(
            self,
            "Edit Planned Monthly Income",
            "Enter the new planned total monthly income:",
            self.planned_income,
            0.01,
            10000000.0,
            2
        )
        if ok and amount > 0:
            self.planned_income = amount
            self.update_diagram()

    def update_node_list(self):
        self.node_list.clear()
        if self.nodes:
            self.node_list.addItems(sorted(self.nodes.keys()))

    def update_asset_list(self):
        self.asset_list.clear()
        for a in self.assets:
            self.asset_list.addItem(f"{a['name']}: ${a['value']:,.0f}")

    def show_add_dialog(self):
        dialog = NodeDialog(self, list(self.nodes.keys()))
        if dialog.exec() == QDialog.Accepted:
            self.process_node_dialog(dialog, None)

    def show_edit_dialog(self):
        item = self.node_list.currentItem()
        if not item:
            QMessageBox.information(self, "Info", "Select a node to edit.")
            return
        label = item.text()
        if label == "Income":
            QMessageBox.information(self, "Info", "The root 'Income' node cannot be edited directly. Use 'Edit Planned Income' to change the planned monthly amount.")
            return
        node = self.nodes[label]
        dialog = NodeDialog(self, list(self.nodes.keys()), edit_node=node)
        if dialog.exec() == QDialog.Accepted:
            self.process_node_dialog(dialog, node)

    def process_node_dialog(self, dialog, edit_node):
        parent_label = dialog.parent_combo.currentText()
        new_label = dialog.name_edit.text().strip()
        if not new_label:
            QMessageBox.warning(self, "Error", "Name required.")
            return
        if new_label != (edit_node.label if edit_node else None) and new_label in self.nodes:
            QMessageBox.warning(self, "Error", "Name already exists.")
            return

        try:
            amount = float(dialog.amount_edit.text())
            if amount <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Error", "Valid positive amount required.")
            return

        group = dialog.group_combo.currentText()
        is_savings = group == "savings"

        if edit_node:  # Edit mode
            old_label = edit_node.label
            parent_node = self.find_parent_node(edit_node)
            # Update link amount
            if parent_node:
                for i, (child, val) in enumerate(parent_node.children):
                    if child is edit_node:
                        parent_node.children[i] = (child, amount)
                        break
            # Update name
            if new_label != old_label:
                edit_node.label = new_label
                del self.nodes[old_label]
                self.nodes[new_label] = edit_node
            # Update group & properties
            edit_node.group = group
            if is_savings:
                edit_node.properties["apr"] = float(dialog.apr_edit.text() or 0)
                edit_node.properties["current_balance"] = float(dialog.balance_edit.text() or 0)
            else:
                edit_node.properties.clear()
        else:  # Add mode
            parent_node = self.nodes[parent_label]
            new_node = Node(new_label, group)
            parent_node.add_child(new_node, amount)
            self.nodes[new_label] = new_node
            if is_savings:
                new_node.properties["apr"] = float(dialog.apr_edit.text() or 0)
                new_node.properties["current_balance"] = float(dialog.balance_edit.text() or 0)

        self.update_node_list()
        self.update_diagram()

    def remove_selected_node(self):
        item = self.node_list.currentItem()
        if not item:
            return
        label = item.text()
        if label == "Income":
            QMessageBox.warning(self, "Error", "Cannot remove root 'Income'.")
            return

        if QMessageBox.question(self, "Confirm", f"Remove '{label}' and subtree?") == QMessageBox.Yes:
            node = self.nodes[label]
            parent = self.find_parent_node(node)
            if parent:
                parent.children = [c for c in parent.children if c[0] is not node]
            to_remove = []
            def collect(n):
                to_remove.append(n.label)
                for c, _ in n.children:
                    collect(c)
            collect(node)
            for l in to_remove:
                del self.nodes[l]

            self.update_node_list()
            self.update_diagram()

    def show_add_asset_dialog(self):
        dialog = AddAssetDialog(self)
        if dialog.exec() == QDialog.Accepted:
            name = dialog.name_edit.text().strip()
            if not name or any(a["name"] == name for a in self.assets):
                QMessageBox.warning(self, "Error", "Valid unique name required.")
                return
            try:
                value = float(dialog.amount_edit.text())
                if value < 0:
                    raise ValueError
            except ValueError:
                QMessageBox.warning(self, "Error", "Valid value required.")
                return
            self.assets.append({"name": name, "value": value})
            self.update_asset_list()
            self.update_diagram()

    def remove_selected_asset(self):
        item = self.asset_list.currentItem()
        if not item:
            return
        name = item.text().split(":")[0].strip()
        self.assets = [a for a in self.assets if a["name"] != name]
        self.update_asset_list()
        self.update_diagram()

    def check_over_allocations(self):
        if not self.root:
            return []
        over = []
        total_allocated = sum(val for _, val in self.root.children)
        if total_allocated > self.planned_income + 0.01:
            over.append("Overall budget")

        inflow = {self.root: self.planned_income}
        def recurse(node):
            node_in = inflow[node]
            node_out = sum(val for _, val in node.children)
            if node_out > node_in + 0.01:
                over.append(node.label)
            for child, val in node.children:
                inflow[child] = val
                recurse(child)
        recurse(self.root)
        return over

    def update_summary_and_warning(self, expense_total, savings_total):
        allocated = sum(val for _, val in self.root.children) if self.root else 0
        unalloc = self.planned_income - allocated

        text = "<b>Budget Summary</b><br><br>"
        text += f"Planned Income: <b>${self.planned_income:,.0f}</b><br>"
        text += f"Total Allocated: <b>${allocated:,.0f}</b><br><br>"
        if unalloc > 0:
            text += f"Surplus: <span style='color:#228B22;'>${unalloc:,.0f}</span><br>"
        elif unalloc < 0:
            text += f"Deficit: <span style='color:red;'>${-unalloc:,.0f}</span><br>"
        text += f"Savings/Investments: <b>${savings_total:,.0f}</b><br>"
        text += f"Expenses: <b>${expense_total:,.0f}</b><br>"

        assets_total = sum(a["value"] for a in self.assets)
        text += f"<br>Standalone Assets Total: <b>${assets_total:,.0f}</b>"

        self.summary_label.setText(text)

        over_nodes = self.check_over_allocations()
        if over_nodes:
            self.warning_label.setText(
                f"⚠ Over-allocation detected in: {', '.join(over_nodes)}"
            )
        else:
            self.warning_label.setText("")

    def build_sankey_data(self):
        all_nodes = collect_nodes(self.root)
        if not all_nodes:
            return [], [], [], [], [], []

        node_index = {node: i for i, node in enumerate(all_nodes)}

        # Inflows
        inflow = {node: 0.0 for node in all_nodes}
        for node in all_nodes:
            for child, val in node.children:
                inflow[child] += val

        # Virtual surplus
        allocated = sum(val for _, val in self.root.children)
        virtual_node = None
        if self.planned_income - allocated > 0.01:
            surplus = self.planned_income - allocated
            virtual_node = Node("Unallocated Surplus", "unallocated")
            self.root.children.append((virtual_node, surplus))

        all_nodes = collect_nodes(self.root)  # re-collect with virtual
        node_index = {node: i for i, node in enumerate(all_nodes)}
        if virtual_node:
            self.root.children.pop()

        # Display values
        display_value = {}
        for node in all_nodes:
            outflow = sum(val for _, val in node.children)
            display_value[node] = outflow if outflow > 0 else inflow.get(node, 0)

        # Labels
        labels = []
        for n in all_nodes:
            if n is self.root:
                labels.append(f"Income<br>Planned: ${self.planned_income:,.0f}<br>Allocated: ${allocated:,.0f}")
            else:
                labels.append(f"{n.label}<br>${display_value[n]:,.0f}")

        # Colors (highlight over-allocated red)
        over_set = set(self.check_over_allocations())
        node_colors = []
        for n in all_nodes:
            if n.label in over_set:
                node_colors.append("#FF0000")  # red for over
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

        # Links
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

        return labels, node_colors, sources, targets, values, link_colors, inflow, all_nodes

    def build_pie_data(self):
        if not self.assets:
            return ["No assets yet"], [1]
        return [a["name"] for a in self.assets], [a["value"] for a in self.assets]

    def update_diagram(self):
        if not self.started or not self.root:
            welcome_html = """
            <div style="display: flex; flex-direction: column; align-items: center; justify-content: center; height: 100vh; background: #f8f8f8; font-family: Arial; text-align: center;">
                <h1>Welcome to Budget Cashflow Visualizer</h1>
                <p style="font-size: 18px; max-width: 800px;">
                    Click the large button to start by entering your planned monthly income.
                </p>
            </div>
            """
            self.view.setHtml(welcome_html)
            return

        labels, node_colors, sources, targets, values, link_colors, inflow, all_nodes = self.build_sankey_data()
        asset_labels, asset_values = self.build_pie_data()

        # Category totals
        category_totals = defaultdict(float)
        def cat_recurse(node):
            for child, val in node.children:
                if not child.children:  # leaf
                    category_totals[child.group] += val
                cat_recurse(child)
        cat_recurse(self.root)
        savings_total = category_totals["savings"]
        expense_total = category_totals["expense"]

        self.update_summary_and_warning(expense_total, savings_total)

        # Expense gauge
        percent = (expense_total / self.planned_income * 100) if self.planned_income > 0 else 0
        gauge_color = "red" if percent > 100 else "darkorange" if percent > 80 else "green"

        # Sankey
        sankey = go.Sankey(
            arrangement="snap",
            node=dict(
                pad=30,
                thickness=40,
                line=dict(color="black", width=1),
                label=labels,
                color=node_colors,
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                color=link_colors,
            ),
        )

        # Gauge
        gauge = go.Indicator(
            mode="gauge+number",
            value=percent,
            number={"suffix": "%"},
            title={"text": "Expenses as % of Income"},
            gauge={
                "axis": {"range": [None, 130]},
                "bar": {"color": gauge_color},
                "steps": [
                    {"range": [0, 80], "color": "lightgreen"},
                    {"range": [80, 100], "color": "yellow"},
                    {"range": [100, 130], "color": "red"}
                ],
            }
        )

        # Pie
        pie = go.Pie(
            labels=asset_labels,
            values=asset_values,
            hole=0.4,
            textinfo="label+value+percent" if self.assets else "label",
        )

        # Projections
        projection_months = self.projection_spin.value()
        projection_traces = []
        if projection_months > 0:
            accumulating = [n for n in all_nodes if not n.children and n.group == "savings"]
            if accumulating:
                time_points = list(range(projection_months + 1))
                total_proj = [0] * (projection_months + 1)
                for node in accumulating:
                    contrib = inflow.get(node, 0)
                    current = node.properties.get("current_balance", 0.0)
                    apr = node.properties.get("apr", 0.0) / 100.0
                    r = apr / 12.0
                    balances = []
                    bal = current
                    balances.append(round(bal, 2))
                    for _ in range(projection_months):
                        bal = bal * (1 + r) + contrib
                        balances.append(round(bal, 2))
                    total_proj = [a + b for a, b in zip(total_proj, balances)]
                    projection_traces.append(go.Scatter(
                        x=time_points,
                        y=balances,
                        mode="lines+markers",
                        name=f"{node.label} Projected"
                    ))
                projection_traces.append(go.Scatter(
                    x=time_points,
                    y=total_proj,
                    mode="lines+markers",
                    name="Total Savings Projected",
                    line=dict(width=5, dash="dot")
                ))

        # Dynamic figure
        rows = 3 + (1 if projection_months > 0 and projection_traces else 0)
        row_heights = [0.55, 0.12, 0.15, 0.18] if rows == 4 else [0.6, 0.15, 0.25]
        specs = [[{"type": "sankey"}],
                 [{"type": "indicator"}],
                 [{"type": "pie"}]]
        if rows == 4:
            specs.append([{"type": "xy"}])

        fig = make_subplots(
            rows=rows,
            cols=1,
            row_heights=row_heights,
            specs=specs,
            subplot_titles=(
                "Monthly Cash Flow",
                "Expense Coverage",
                "Standalone Assets",
                "Projected Savings Growth" if rows == 4 else None
            ),
            vertical_spacing=0.08,
        )

        fig.add_trace(sankey, row=1, col=1)
        fig.add_trace(gauge, row=2, col=1)
        fig.add_trace(pie, row=3, col=1)
        if rows == 4:
            for trace in projection_traces:
                fig.add_trace(trace, row=4, col=1)
            fig.update_xaxes(title_text="Months", row=4, col=1)
            fig.update_yaxes(title_text="Balance ($)", row=4, col=1)

        fig.update_layout(
            title_text="Personal Budget Visualization",
            title_x=0.5,
            font_size=13,
            height=1200,
            margin=dict(t=100, b=50),
        )

        html = fig.to_html(include_plotlyjs="cdn")
        self.view.setHtml(html)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    # Optional: Better dark mode support on some platforms
    app.setStyle("Fusion")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())