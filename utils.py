import os
import configparser
import shutil
from time import sleep

from browser_factory import (
    BrowserFactory,
    FIREFOX,
    FIREFOX_INIT_PATH,
    FIREFOX_WORK_DIR,
    FIREFOX_EXE_PATH,
    FIREFOX_PROFILE_PATH,
)


def read_firefox_init():
    config = configparser.ConfigParser()
    config.read(FIREFOX_INIT_PATH)
    profiles = []
    for k, v in config.items():
        if k.startswith("Profile") and v.get("NAME") != "default-release":
            profiles.append((v.get("NAME"), v.get("PATH")))
    return profiles


def create_if_not_exist(browser_type: int, max_index: int) -> (int, str):
    browser_factory = BrowserFactory(browser_type)
    _path = ""
    if browser_type == FIREFOX:
        profiles = read_firefox_init()
        while True:
            profile_name = f"Profile_{max_index}"
            if profile_name not in [profile[0] for profile in profiles]:
                import subprocess

                subprocess.run([FIREFOX_EXE_PATH, "-CreateProfile", profile_name])
                sleep(0.2)
                new_profiles = read_firefox_init()
                for profile in new_profiles:
                    name, path = profile
                    if name == profile_name:
                        _path = path.split("/")[1]
                        _full_path = os.path.join(FIREFOX_PROFILE_PATH, _path)
                        shutil.rmtree(_full_path)
                        sleep(0.1)
                        os.makedirs(_full_path)
                        break
                break
            max_index += 1
    else:
        while True:
            profile_name = f"Profile {max_index}"
            profile_path = os.path.join(
                browser_factory.get_profile_folder(), profile_name
            )
            if not os.path.exists(profile_path):
                os.makedirs(profile_path)
                break

            max_index += 1

    return max_index, _path
