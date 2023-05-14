import os
import queue
import sys
import threading
import time
from time import sleep

from PyQt6.QtCore import QThread, pyqtSignal
from PyQt6.QtGui import QIntValidator
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
    QMessageBox,
)
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class CreateProfileThread(QThread):
    finished = pyqtSignal()

    def __init__(self, num_profile):
        super().__init__()
        self.num_profile = num_profile

    def run(self):
        # tạo driver
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-extensions")
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")
        profile_dir = os.getcwd() + f"/profiles/profile_{self.num_profile}"
        if not os.path.exists(profile_dir):
            os.makedirs(profile_dir)
        try:
            options.add_argument(f"--user-data-dir={profile_dir}")

            webdriver.Chrome(
                service=Service(ChromeDriverManager().install()),
                options=options,
            )
            sleep(0.5)
        except Exception as e:
            print(e)

        self.finished.emit()


class ThreadPool:
    def __init__(self, num_threads):
        self.task_queue = queue.Queue()
        self.threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=self.run_tasks)
            self.threads.append(thread)
            thread.start()

    def add_task(self, task):
        self.task_queue.put(task)

    def run_tasks(self):
        while self.task_queue.not_empty:
            task = self.task_queue.get()
            task.finished.connect(self.alert)
            task.run()
            self.task_queue.task_done()

    def alert(self):
        ...


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        hbox1 = QHBoxLayout()
        label = QLabel("Browser")
        self.combo = QComboBox()
        self.combo.addItem("Chrome", 1)
        self.combo.addItem("Fire Fox", 2)
        self.combo.addItem("Edge Dev", 3)
        hbox1.addWidget(label)
        hbox1.addWidget(self.combo)
        vbox.addLayout(hbox1)

        hbox2 = QHBoxLayout()
        self.radio1 = QRadioButton("Tạo mới profile")
        self.radio1.setChecked(True)
        self.radio2 = QRadioButton("Thêm profile")
        hbox2.addWidget(self.radio1)
        hbox2.addWidget(self.radio2)
        vbox.addLayout(hbox2)

        hbox3 = QHBoxLayout()
        label = QLabel("Số profile")
        self.input = QLineEdit()
        self.input.setValidator(QIntValidator(1, 100))
        hbox3.addWidget(label)
        hbox3.addWidget(self.input)
        vbox.addLayout(hbox3)

        hbox3 = QHBoxLayout()
        label = QLabel("Số luồng")
        self.comboThread = QComboBox()
        self.comboThread.addItems(["2", "4", "6", "8", "10"])
        hbox1.addWidget(label)
        hbox1.addWidget(self.comboThread)
        vbox.addLayout(hbox3)

        self.button = QPushButton("Generate")
        self.button.clicked.connect(self.run_task)
        vbox.addWidget(self.button)

        self.setLayout(vbox)
        self.setWindowTitle("Browser Generate")

        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Icon.Information)

    def run_task(self):
        start_time = time.time()
        browser = self.combo.currentData()
        option = "Tạo mới" if self.radio1.isChecked() else "Thêm"
        num_profiles = int(self.input.text())
        num_threads = int(self.comboThread.currentText())

        if browser == 1 and self.radio1.isChecked():
            self.button.setDisabled(True)
            thread_pool = ThreadPool(num_threads=num_threads)
            # tạo thread để tạo các profile
            for profile in range(num_profiles):
                thread_pool.add_task(CreateProfileThread(profile + 1))
            thread_pool.task_queue.join()
            if thread_pool.task_queue.empty():
                time_excute = time.time() - start_time
                self.button.setDisabled(False)
                self.msgBox.setText(f"Hoàn thành trong: {time_excute} giây")
                self.msgBox.exec()

        else:
            self.msgBox.setText("Chức năng chưa thực hiện!")
            self.msgBox.exec()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    app.exec()
