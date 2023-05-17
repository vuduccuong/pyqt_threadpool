import os
import queue
import sys
import threading
import time
import zipfile

import winshell
from win32com.client import Dispatch
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
    QFileDialog,
)

from browser_factory import BROWSER, BrowserFactory


lock = threading.Lock()


class CreateProfileThread(QThread):
    finished = pyqtSignal()

    def __init__(self, profile_name, zip_file_path, browser_type):
        super().__init__()
        self.profile_name = profile_name
        self.zip_file_path = os.path.join(zip_file_path)
        self.browser_type = browser_type

    def run(self):
        try:
            # Extract my profile to new profile
            try:
                print(f"Bắt đầu giải nén cho {self.profile_name}")
                browser_profile_path = BrowserFactory(self.browser_type).get_profile_folder()
                browser_exe_path, browser_work_dir = BrowserFactory(self.browser_type).get_browser()
                with zipfile.ZipFile(self.zip_file_path, 'r') as zf:
                    zf.extractall(os.path.join(browser_profile_path, self.profile_name))
                print("Giải nén xong")
            except Exception as e:
                print(e)
                return
            # Create Shotcut
            desktop = winshell.desktop()
            path = desktop + f"\\{self.profile_name}-{BROWSER.get(self.browser_type)}.lnk"
            target = browser_exe_path
            icon = browser_exe_path
            shell = Dispatch('WScript.Shell')
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.Arguments = f"--profile-directory=\"{self.profile_name}\""
            shortcut.WorkingDirectory = browser_work_dir
            shortcut.IconLocation = icon

            shortcut.save()
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


def create_if_not_exist(browser_type: int, max_index: int) -> int:
    browser_factory = BrowserFactory(browser_type)
    while True:
        profile_name = f"Profile {max_index}"
        profile_path = os.path.join(browser_factory.get_profile_folder(), profile_name)
        if not os.path.exists(profile_path):
            os.makedirs(profile_path)
            break

        max_index += 1
    return max_index


class MyWidget(QWidget):
    def __init__(self):
        super().__init__()

        self.init_ui()

    def init_ui(self):
        vbox = QVBoxLayout()

        h_box_dialog = QHBoxLayout()
        self.setWindowTitle('Chọn profile của bạn')
        self.setGeometry(300, 300, 300, 100)

        self.zip_file_path = QLineEdit(self)
        self.zip_file_path.setGeometry(10, 10, 200, 30)
        self.zip_file_path.setReadOnly(True)

        self.button = QPushButton('Select File', self)
        self.button.setGeometry(220, 10, 70, 30)
        self.button.clicked.connect(self.show_file_dialog)

        h_box_dialog.addWidget(self.zip_file_path)
        h_box_dialog.addWidget(self.button)
        vbox.addLayout(h_box_dialog)

        hbox1 = QHBoxLayout()
        label = QLabel("Browser")
        self.combo = QComboBox()
        for k, v in BROWSER.items():
            self.combo.addItem(v, k)
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
        self.input.setText("1")
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
        self.setWindowTitle("Browser Profile Generate")

        self.msgBox = QMessageBox()
        self.msgBox.setIcon(QMessageBox.Icon.Information)

    def run_task(self):
        start_time = time.time()
        browser = self.combo.currentData()
        num_profiles = int(self.input.text())
        num_threads = int(self.comboThread.currentText())
        if num_threads < num_profiles:
            num_threads = num_profiles
        zip_file_path = self.zip_file_path.text()

        if not zip_file_path:
            self.msgBox.setText("Chọn file Profile zip!")
            self.msgBox.exec()
            return

        if self.radio1.isChecked():
            self.button.setDisabled(True)
            thread_pool = ThreadPool(num_threads=num_threads)
            # tạo thread để tạo các profile
            profile_id = create_if_not_exist(browser_type=browser, max_index=0)
            for index in range(num_profiles):
                profile_name = f"Profile {profile_id}"
                thread_pool.add_task(CreateProfileThread(profile_name, zip_file_path, browser))
                profile_id += 1
                if index < num_profiles - 1:
                    profile_id = create_if_not_exist(browser_type=browser, max_index=profile_id)
            thread_pool.task_queue.join()
            if thread_pool.task_queue.empty():
                time_excute = time.time() - start_time
                self.msgBox.setText(f"Hoàn thành trong: {time_excute} giây")
                self.msgBox.exec()
        else:
            self.msgBox.setText("Chức năng chưa thực hiện!")
            self.msgBox.exec()

        self.button.setDisabled(False)

    def show_file_dialog(self):
        file_dialog = QFileDialog()
        file_path = file_dialog.getOpenFileName(self, 'Select File', directory=os.getcwd())[0]
        if file_path:
            self.zip_file_path.setText(file_path)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    widget = MyWidget()
    widget.show()
    app.exec()
