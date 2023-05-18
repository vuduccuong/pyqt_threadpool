import sys
from PyQt6.QtWidgets import QApplication
from ui.main_app import MyWidget


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    app.exec()
