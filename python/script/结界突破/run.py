import time

import python.core.base.cv as cv

import python.core.base.mouse as mouse
import python.core.base.keyboard as keyboard
import python.core.base.window as win
import mss
import numpy as np
from python.core.base.structs import BOX, POINT

mss = mss.mss()
rect, hwnd = win.get_rect_with_title('主账号')
# 置信度

# 失败次数
count = 4
start = f'./img/step1.png'
fight = f'./img/step2.png'
awad = f'./img/step3.png'
success = f'./img/success.png'
fail = f'./img/fail.png'
sure = f'./img/sure.png'


def screenshot():
    """

    :return:
    """
    img = np.array(mss.grab(rect))
    cv.cvtColor(img)
    return cv.cvtColor(img)


def check_fail():
    target = screenshot()
    template = cv.imread(fail)
    res = cv.get_res(target=target, template=template)
    height, width = template.shape[:2]
    loc = np.where(res >= 0.90)
    if len(loc[0]) >= count:
        # 失败次数合格
        return True
    else:
        do_start()


def do_start():
    target = screenshot()
    template = cv.imread(start)
    _threshold, pt = cv.do_match(target=target, template=template)
    height, width = template.shape[:2]
    if _threshold >= 0.86:
        p = get_cent_xy(avg=pt, box=BOX(height=height, width=width))
        mouse.lift_click(p)
        click_fight()
        keyboard.keys('esc')



def click_sure():
    target = screenshot()
    template = cv.imread(sure)
    _threshold, pt = cv.do_match(target=target, template=template)
    height, width = template.shape[:2]
    if _threshold >= 0.90:
        p = get_cent_xy(avg=pt, box=BOX(height=height, width=width))
        mouse.lift_click(p)
        return True


def click_fight():
    target = screenshot()
    template = cv.imread(fight)
    _threshold, pt = cv.do_match(target=target, template=template)
    height, width = template.shape[:2]
    if _threshold >= 0.90:
        p = get_cent_xy(avg=pt, box=BOX(height=height, width=width))
        mouse.lift_click(p)
        time.sleep(1)
        return True


def get_cent_xy(avg, box):
    """

    :param avg:
    :param box:
    :return:
    """
    lower_right = (avg[0] + box.width, avg[1] + box.height)
    x = (int((avg[0] + lower_right[0]) / 2))
    y = (int((avg[1] + lower_right[1]) / 2))
    return POINT(x=x, y=y)


def execute():
    while True:
        target = screenshot()
        # 只打徽章数等于5的
        template = cv.imread(start)
        res = cv.get_res(target=target, template=template)
        height, width = template.shape[:2]
        # 取匹配程度大于%90的坐标
        threshold = 0.88
        # np.where返回的坐标值(x,y)是(h,w)，注意h,w的顺序
        loc = np.where(res >= threshold)
        for pt in zip(*loc[::-1]):
            bottom_right = (pt[0] + width, pt[1] + height)
            cv.rectangle(target, pt, BOX(height=height, width=width))
            print(pt, bottom_right)
        cv.show('11', img=target)
        if cv.waitKey(25) & 0xFF == ord("q"):
            cv.destroyAllWindows()
            break


def run():
    # check_fail()
    execute()


run()
