import os
import zipfile
import queue
import threading


import winshell
from PyQt6.QtCore import QThread, pyqtSignal
from win32com.client import Dispatch

from browser_factory import BrowserFactory, BROWSER, FIREFOX


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
            # task.finished.connect()
            task.run()
            self.task_queue.task_done()


class CreateProfileThread(QThread):
    finished = pyqtSignal()

    def __init__(self, profile_name, zip_file_path, browser_type, path):
        super().__init__()
        self.profile_name = profile_name
        self.zip_file_path = os.path.join(zip_file_path)
        self.browser_type = browser_type
        self.path = path

    def run(self):
        try:
            # Extract my profile to new profile
            try:
                browser_factory = BrowserFactory(self.browser_type)
                browser_profile_path = browser_factory.get_profile_folder()
                _name = self.profile_name
                if self.browser_type == FIREFOX:
                    _name = self.path
                browser_exe_path, browser_work_dir = browser_factory.get_browser()
                with zipfile.ZipFile(self.zip_file_path, "r") as zf:
                    zf.extractall(os.path.join(browser_profile_path, _name))
                print("Giải nén xong")
            except Exception as e:
                print(e)
                return
            # Create Shotcut
            desktop = winshell.desktop()
            path = (
                desktop + f"\\{self.profile_name}-{BROWSER.get(self.browser_type)}.lnk"
            )
            target = browser_exe_path
            icon = browser_exe_path
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortCut(path)
            shortcut.Targetpath = target
            shortcut.Arguments = browser_factory.get_arg(self.profile_name)
            shortcut.WorkingDirectory = browser_work_dir
            shortcut.IconLocation = icon

            shortcut.save()
        except Exception as e:
            print(e)
        self.finished.emit()
