import sys
from PySide6.QtWidgets import QApplication
from cashflow import App


def main():
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    window = App()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
