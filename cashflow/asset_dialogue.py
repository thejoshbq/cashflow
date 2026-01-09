# asset_dialogue.py

from PySide6.QtWidgets import (QDialog, QFormLayout, QLineEdit, QDialogButtonBox)
from PySide6.QtGui import QDoubleValidator


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