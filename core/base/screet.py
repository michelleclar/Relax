import pyautogui
"""
按键操作 屏幕操作
"""

def do_screenshot(screenshot_path, region):
    """
    截图
    :param screenshot_path: 截图存放路径
    :param region: 截图范围
    :return:
    """
    # 屏幕截图
    pyautogui.screenshot(screenshot_path, region)


def left_click(avg):
    """
    在指定坐标左键单击
    :param avg:
    :return:
    """
    pyautogui.click(avg[0], avg[1], button='left')


def right_click(avg):
    """
    在指定坐标右键单击
    :param avg:
    :return:
    """
    pyautogui.click(avg[0], avg[1], button='right')


def current_resolution():
    """
    获取当前屏幕分辨率
    :return:
    """
    return pyautogui.size()


def keys(key):
    """
    模拟键盘输入
    :param key:
    :return:
    """
    pyautogui.press(key)

def get_region_by_title(win_title:str):
    """
    根据窗口标题获取到实际窗口
    :param win_title:
    :return:region
    """
    win = pyautogui.getWindowsWithTitle(win_title)
    return win[0].box
