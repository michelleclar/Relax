import os
import glob
import time as t
import numpy as np
from concurrent.futures import ThreadPoolExecutor, wait


# 生成随机字符串
def generate_random_string(length=8):
    import random
    import string
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


# 得到中点坐标
def get_cent_xy(avg, box):
    height, width = box
    lower_right = (avg[0] + width, avg[1] + height)
    return [
        (int((avg[0] + lower_right[0]) / 2)),
        (int((avg[1] + lower_right[1]) / 2))]


def get_random_xy(avg, box):
    import random
    height, width = box
    x, y = avg
    x += random.uniform(0, height)
    y += random.uniform(0, width)
    return [x, y]


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
