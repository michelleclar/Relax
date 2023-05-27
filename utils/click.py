import time

import pyautogui


def click(var_avg):
    """
    :param var_avg:
    :return:
    """
    pyautogui.click(var_avg[0], var_avg[1], button='left')
    time.sleep(1)