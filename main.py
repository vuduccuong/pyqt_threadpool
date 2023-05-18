import sys
from PyQt6.QtWidgets import QApplication

from main_app import MyWidget

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        widget = MyWidget()
        widget.show()
        app.exec()
    except Exception as e:
        raise e
