import os
import glob
import time as t
import numpy as np
import pyautogui
import cv2
from core.base import image, screet
from concurrent.futures import ThreadPoolExecutor, wait
from core.base.build import Build, ClickStrategy, InputKeyStrategy, Strategy, MatchRule, ScriptArgs
from core.base.structs import POINT


# 具体执行逻辑
def do_execute(node: ScriptArgs, screenshot):
    rule = type(node.match_rule)
    match rule:
        case MatchRule.Template:
            """模板匹配"""
            rule = node.match_rule
            template = image.cache_imread(f"../imgs/{rule.template_name}.png")

            threshold, min_loc = image.do_match(screenshot, template)
            if threshold > rule.threshold:
                # 匹配成功
                height, width = template.shape[:2]
                strategy = type(node.strategy)
                match strategy:
                    case type(ClickStrategy):
                        point = get_xy(node.strategy, min_loc, [height, width])
                        click(point, node.strategy.button)
                    case type(InputKeyStrategy):
                        send_keys()
            else:
                # 匹配失败 retry
                pass

        case MatchRule.Ocr:
            # Ocr
            pass
            """ocr"""


# 生成随机字符串
def generate_random_string(length=8):
    import random
    import string
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


def click(point: POINT, button: str):
    pyautogui.click(point.x, point.y, button=button)


# 得到中点坐标
def get_xy(strategy: ClickStrategy, min_loc, box):
    _strategy = strategy.strategy
    point = POINT()
    match _strategy:
        case Strategy.CENTER:
            res = get_cent_xy(min_loc, box)
            point = POINT(x=res[0], y=res[1])
        case Strategy.RANDOM:
            res = get_random_xy(min_loc, box)
            point = POINT(x=res[0], y=res[1])
        case Strategy.WITHOUT:
            # 匹配之外的点
            pass
    # TODO 进行随机点偏移
    point.x += strategy.offset.x
    point.y += strategy.offset.y
    return point

def send_keys():
    pass

def get_cent_xy(avg, box):
    height, width = box
    lower_right = (avg[0] + width, avg[1] + height)
    x = (int((avg[0] + lower_right[0]) / 2))
    y = (int((avg[1] + lower_right[1]) / 2))
    return POINT(x=x, y=y)


def get_random_xy(avg, box):
    import random
    height, width = box
    x, y = avg
    x += random.uniform(0, height)
    y += random.uniform(0, width)
    return POINT(x=x, y=y)


# time
# 得到当前时间
def get_current_timestamp():
    return t.time()


# 时间元组
def get_current_struct_time():
    return t.localtime()


# 格式化当前时间
def format_time(format, time=None):
    if time is None:
        time = t.localtime()
    return t.strftime(format, time)


# thread
# 任务池化
def task_pool(*args):
    tasks = []
    for arg in args:
        task = ThreadPoolExecutor().submit(*arg)
        tasks.append(task)
        sleep(1)

    wait(tasks)


# 休眠
def sleep(time):
    t.sleep(max(0, time))


# numpy
# 数组初始化
def init_arr_obj(length, obj):
    return np.full(length, obj)


def clear(folder_path, type=None):
    if type is None:
        type = ['*.png', '*.jpg']
    files = glob.glob(os.path.join(folder_path, *type))
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {str(e)}")
