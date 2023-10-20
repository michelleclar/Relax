from build import Build, MatchRule, ScriptArgs, ClickStrategy, InputKeyStrategy, Strategy
from commons import exception
from core.base import image, screet, log
from utils import util
from structs import POINT
from time import time, localtime, strftime, sleep
from concurrent.futures import ThreadPoolExecutor, wait
from os import path, remove
from numpy import full
from glob import glob
from pyautogui import click

# 执行方法
logger = log.get_logger()
execute = None

# 重试时间
RETRYTIME = None
# 疑似点击失败 重试次数
RETRYCOUNT = None
# 运行次数
TASKLOOP = None
# 监控
MONITOR = None

DEBUG = None

GUARD = None


def init_execute_processor():
    from yaml import load, Loader
    # 重试时间
    global RETRYTIME
    # 疑似点击失败 重试次数
    global RETRYCOUNT
    # 运行次数
    global TASKLOOP
    # 监控
    global MONITOR

    global DEBUG

    global GUARD
    logger.info("正在读取配置")
    with open("../config.yml", "r") as f:
        ayml = load(f.read(), Loader=Loader)
        execute_consts = ayml["execute"]

        RETRYTIME = execute_consts['RetryTime']
        RETRYCOUNT = execute_consts['RetryCount']
        TASKLOOP = execute_consts['TaskLoop']
        MONITOR = execute_consts['Monitor']

        switch_consts = ayml["switch"]
        MONITOR = switch_consts["Debug"]
        DUARD = switch_consts["Guard"]
    logger.info(f'配置内容为{ayml}')
    global execute
    execute = Execute(retry_time=RETRYTIME, retry_count=RETRYCOUNT, task_loop=TASKLOOP, monitor=MONITOR)


# 具体执行逻辑
def do_execute(node: ScriptArgs, screenshot):
    match node.match_rule:
        case MatchRule.Template:
            """模板匹配"""
            rule = node.match_rule
            template = image.cache_imread(f"../imgs/{rule.template_name}.png")

            threshold, min_loc = image.do_match(screenshot, template)
            if threshold > rule.threshold:
                # 匹配成功
                height, width = template.shape[:2]
                strategy = node.strategy
                match strategy:
                    case ClickStrategy.mro():
                        point = util.get_xy(node.strategy, min_loc, [height, width])
                        util.click(point, node.strategy.button)
                    case InputKeyStrategy.mro():
                        util.send_keys()
            else:
                # 匹配失败 retry
                pass

        case MatchRule.Ocr:
            # Ocr
            pass
            """ocr"""


class Execute(object):
    """运行构建器构建的参数"""

    def __init__(self, retry_time, retry_count, task_loop, monitor):
        # 任务循环次数
        self.retry_time = retry_time
        self.retry_count = retry_count
        self.task_loop = task_loop
        self.monitor = monitor

    def execute(self, task: [Build.BuildTaskArgs]):
        """根据类型执行不同的执行方式"""
        task_type = type(task)
        match task_type:
            case Build.BuildTaskArgs:
                self.execute_task_args(task)
            case _:
                logger.error(f'不支持此类型：{task_type}')

    def do_screenshot(self, region, screenshot_path: str):
        """截图操作,后续可能会处理成流"""
        screet.do_screenshot(screenshot_path, region)
        return image.imread(screenshot_path)

    def init_screenshot(self, win_title: str):
        """截图预热"""
        screenshot_name = "screenshot" + util.generate_random_string(4)
        # 进行区域处理
        region = screet.get_region_by_title(win_title)
        screenshot_path = f"../imgs/screenshot/{screenshot_name}.png"
        return region, screenshot_path

    # TODO 将这个执行转化成类 用来方便参数传递 
    def execute_task_args(self, task: Build.BuildTaskArgs):
        """正式开始执行"""
        # 初始化等待时间列表
        times = util.init_arr_obj(len(task.nodes) + 1, -1)
        # TODO 将image和screet 进行整合
        region, screenshot_path = self.init_screenshot(task.win_title)

        temp = util.get_current_timestamp()
        nodes = task.nodes
        for c in range(self.task_loop):
            start_time = util.get_current_timestamp()
            while util.get_current_timestamp() - start_time < self.retry_time:
                for i, node in enumerate(nodes):
                    start_time = util.get_current_timestamp()
                    scrreenshot = self.do_screenshot(region=region, screenshot_path=screenshot_path)
                    try:
                        do_execute(node, screenshot=scrreenshot)
                    except exception as e:
                        pass
                    util.sleep(times[i + 1])
                    start = util.get_current_timestamp()

                    times[i] = (
                        times[i]
                        if (times[i] != -1) and ((times[i] - start - temp) < 0)
                        else start - temp
                    )
                    temp = start


# 封装一些常用方法
def generate_random_string(length=8):
    import random
    import string
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


def _click(point: POINT, button: str):
    click(point.x, point.y, button=button)


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
    return time()


# 时间元组
def get_current_struct_time():
    return localtime()


# 格式化当前时间
def format_time(format, time=None):
    if time is None:
        time = localtime()
    return strftime(format, time)


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
def _sleep(time):
    sleep(max(0, time))


# numpy
# 数组初始化
def init_arr_obj(length, obj):
    return full(length, obj)


def clear(folder_path, type=None):
    if type is None:
        type = ['*.png', '*.jpg']
    files = glob(path.join(folder_path, *type))
    for file in files:
        try:
            remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {str(e)}")
