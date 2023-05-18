import os
import zipfile

import winshell
from PyQt6.QtCore import QThread, pyqtSignal
from win32com.client import Dispatch

from browser_factory import BrowserFactory, BROWSER


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
                browser_profile_path = BrowserFactory(
                    self.browser_type
                ).get_profile_folder()
                browser_exe_path, browser_work_dir = BrowserFactory(
                    self.browser_type
                ).get_browser()
                with zipfile.ZipFile(self.zip_file_path, "r") as zf:
                    zf.extractall(os.path.join(browser_profile_path, self.profile_name))
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
            shortcut.Arguments = f'--profile-directory="{self.profile_name}"'
            shortcut.WorkingDirectory = browser_work_dir
            shortcut.IconLocation = icon

            shortcut.save()
        except Exception as e:
            print(e)
        self.finished.emit()
