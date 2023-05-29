import time

import pyautogui

from utils.get_vector import get_xy


def click(var_avg):
    """
    :param var_avg:
    :return:
    """
    pyautogui.click(var_avg[0], var_avg[1], button='left')
    time.sleep(1)

def click_current(second=1):
    time.sleep(second)
    pyautogui.click()
def auto_click(img_model_path, name):
    avg = get_xy(img_model_path, False)
    print(f'正在点击{name},坐标xy:{avg[0], avg[1]}')
    click(avg)