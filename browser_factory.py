import os

CHROME = 1
FIREFOX = 2
EDGE = 3
BROWSER = {
    CHROME: 'Chrome',
    FIREFOX: 'Firefox',
    EDGE: 'Edge'
}

CHROME_WORK_DIR = "C:\\Program Files\\Google\\Chrome\\Application\\"
CHROME_EXE_PATH = "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe"
CHROME_PROFILE_PATH = os.path.join(os.path.expanduser('~'), "AppData\\Local\\Google\Chrome\\User Data")

FIREFOX_WORK_DIR = "C:\\Program Files\\Mozilla Firefox\\"
FIREFOX_EXE_PATH = "C:\\Program Files\\Mozilla Firefox\\firefox.exe"
FIREFOX_PROFILE_PATH = os.path.join(os.path.expanduser('~'), "AppData\\Roaming\\Mozilla\\Firefox\\Profiles")

EDGE_WORK_DIR = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\"
EDGE_EXE_PATH = "C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
EDGE_PROFILE_PATH = os.path.join(os.path.expanduser('~'), "AppData\\Local\\Microsoft\\Edge\\User Data")


class BrowserFactory:
    def __init__(self, browser_type: int):
        self.browser_type = browser_type

    def get_browser(self):
        return {
            CHROME: (CHROME_EXE_PATH, CHROME_WORK_DIR),
            FIREFOX: (FIREFOX_EXE_PATH, FIREFOX_WORK_DIR),
            EDGE: (EDGE_EXE_PATH, EDGE_WORK_DIR),
        }.get(self.browser_type)

    def get_profile_folder(self):
        return {
            CHROME: CHROME_PROFILE_PATH,
            FIREFOX: FIREFOX_PROFILE_PATH,
            EDGE: EDGE_PROFILE_PATH
        }.get(self.browser_type)
