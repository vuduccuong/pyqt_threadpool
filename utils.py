import os

from browser_factory import BrowserFactory


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
