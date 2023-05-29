import time

import pyautogui


def keys(keys, second=1):
    time.sleep(second)
    for key in keys:
        pyautogui.press(key)
        time.sleep(second)