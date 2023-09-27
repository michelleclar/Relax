"""
此包只能包含 操作屏幕的方法
"""
import pyautogui


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
