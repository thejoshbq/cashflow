# node_dialogue.py

from PySide6.QtWidgets import (
    QLabel, QDialog, QFormLayout,
    QComboBox, QLineEdit, QDialogButtonBox
)
from PySide6.QtGui import QDoubleValidator


class NodeDialog(QDialog):
    def __init__(self, parent=None, current_labels=None, edit_node=None):
        super().__init__(parent)
        self.edit_node = edit_node
        self.old_label = edit_node.label if edit_node else None
        self.setWindowTitle("Edit Node" if edit_node else "Add New Node")
        layout = QFormLayout(self)
        self.parent_combo = QComboBox()
        if current_labels:
            self.parent_combo.addItems(sorted(current_labels))
        self.parent_combo.setEnabled(edit_node is None)
        if edit_node:
            parent = self.find_parent(edit_node)
            if parent:
                self.parent_combo.setCurrentText(parent.label)
        layout.addRow("Parent Node:", self.parent_combo)
        self.name_edit = QLineEdit()
        if edit_node:
            self.name_edit.setText(edit_node.label)
        layout.addRow("Node Name:", self.name_edit)
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
        self.group_combo = QComboBox()
        self.group_combo.addItems(["intermediate", "savings", "expense", "holding"])
        if edit_node:
            self.group_combo.setCurrentText(edit_node.group)
        layout.addRow("Node Type (color):", self.group_combo)
        self.apr_label = QLabel("Annual Interest Rate (%):")
        self.apr_edit = QLineEdit()
        self.apr_edit.setValidator(QDoubleValidator(0.0, 20.0, 2))
        layout.addRow(self.apr_label, self.apr_edit)
        self.balance_label = QLabel("Current Balance ($):")
        self.balance_edit = QLineEdit()
        self.balance_edit.setValidator(QDoubleValidator(0.0, 1000000000.0, 2))
        layout.addRow(self.balance_label, self.balance_edit)
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

