import time as t

import pyautogui

from utils.get_vector import get_xy


def click(var_avg, time=0):
    """
    :param var_avg:
    :return:
    """
    pyautogui.click(var_avg[0], var_avg[1], button='left')
    t.sleep(time)


def click_current(second=1):
    t.sleep(second)
    pyautogui.click()


def auto_click(img_model_path, name, time=0, x=0, y=0):
    avg = get_xy(img_model_path)
    if avg == None:
        print(f'没有匹配{name}')
        return False
    print(f'正在点击{name},坐标xy:{avg[0], avg[1]}')
    x += avg[0]
    y += avg[1]
    click((x, y), time)
    return True
def auto_click(img_model_path, name, time=0, x=0, y=0,region=(0,0,2560,1440)):
    avg = get_xy(img_model_path,region)
    if avg == None:
        print(f'没有匹配{name}')
        return False
    print(f'正在点击{name},坐标xy:{avg[0], avg[1]}')
    x += avg[0]
    y += avg[1]


    click((x, y), time)
    return True
