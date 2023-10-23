import mss
from collections import deque, namedtuple
from concurrent.futures import ThreadPoolExecutor, wait
import time as t

import numpy as np
from enum import Enum
from commons import exception
from core.base import cv, simulate, log
from core.base.structs import DAG, OFFSET, POINT, BOX

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
POOL = ThreadPoolExecutor(max_workers=10)


def init_execute_processor():
    from yaml import load, Loader
    logger.info("正在读取配置")
    with open("config.yml", "r", encoding='utf-8') as f:
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
        ayml = load(f.read(), Loader=Loader)
        execute_consts = ayml["execute"]

        RETRYTIME = execute_consts['RetryTime']
        RETRYCOUNT = execute_consts['RetryCount']
        TASKLOOP = execute_consts['TaskLoop']
        MONITOR = execute_consts['Monitor']

        switch_consts = ayml["switch"]
        DEBUG = switch_consts["Debug"]
        GUARD = switch_consts["Guard"]
    logger.info(f'配置内容为{ayml}')

    return Execute(retry_time=RETRYTIME, retry_count=RETRYCOUNT, task_loop=TASKLOOP, monitor=MONITOR)


# ===========================================================

Edge = namedtuple('Edge', ['ind_node', 'dep_node'])


# 任务参数设置  将点击延迟和随机点击迁移到点击事件名中
# 整体参数结构设计
# 匹配规则   枚举值，ocr匹配:需要有匹配的文字参数 模板匹配:需要模板图片名字
# 点击事件名，点击事件

# 脚本运行参数 点击事件名（元组：事件名，枚举值：中心，随即，不点击匹配位置） 匹配规则（单独参数）是否启用防检测机制
class MatchRule(object):
    """
    ocr: 文字
    template: 图片名
    """

    def ocr(self, text):
        return self.Ocr(text=text)

    def template(self, template_name):
        return self.Template(template_name=template_name)

    class Ocr(object):
        def __init__(self, text):
            self.text = text

        def __str__(self):
            return f'Ocr(text={self.text})'

    class Template(object):
        def __init__(self, template_name, threshold=None):
            self.template_name = template_name
            self.threshold = threshold if threshold is not None else 0.9

        def __str__(self):
            return f'Template(template_name={self.template_name})'


class Policy(Enum):
    CENTER = 1  # 点击匹配的图像中心
    RANDOM = 2  # 在匹配区域最近点击
    WITHOUT = 3  # 点击匹配区域之外的地方


class Button(Enum):
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"
    PRIMARY = "primary"
    SECONDARY = "secondary"


class Strategy(object):
    class ClickStrategy(object):
        """点击策略"""

        def __init__(self, policy=Policy.CENTER, offset=OFFSET(x=0, y=0), button=Button.LEFT):
            self.policy = policy
            self.offset = offset
            self.button = button

        def __str__(self):
            return f'ClickStrategy(strategy={self.policy}, offset={self.offset}, button={self.button})'

    class InputKeyStrategy(object):
        """按键操作策略"""

        def __init__(self, key='ESC'):
            self.key = key

        def __str__(self):
            return f'InputKeyStrategy(keys={self.key})'


class ScriptArgs(object):
    """节点参数"""
    _auto_increment_weight = 0

    def __init__(self, task_name: any, strategy: [Strategy.InputKeyStrategy, Strategy.ClickStrategy],
                 match_rule: [MatchRule.Ocr, MatchRule.Template]
                 , weight=None):

        self.task_name = task_name
        self.match_rule = match_rule
        self.strategy = strategy
        if weight is not None:
            self.weight = weight
        else:
            # 自增weight，并将其分配给实例
            ScriptArgs._auto_increment_weight += 1
            self.weight = ScriptArgs._auto_increment_weight

    def __eq__(self, other):
        if not isinstance(other, ScriptArgs):
            return False
        return self.task_name == other.task_name

    def __hash__(self):
        return hash(self.task_name)

    def __str__(self):
        return f'ScriptArgs(task_name={self.task_name}, match_rule={self.match_rule}, strategy={self.strategy})'


class Build(object):
    def __init__(self):
        self.win_titles = set()
        pass

    """通用构建器"""

    def BuildTaskArgs(self, win_title: str):
        self.win_titles.add(win_title)
        return BuildTaskArgs(win_title=win_title)


class BuildTaskArgs(object):
    """任务流构建器"""

    def __init__(self, win_title: str, task_loop: int):
        self.dag = DAG()
        self.win_title = win_title
        self.nodes = set()
        self.edges = set()
        self.task_loop = task_loop

    def get_win_title(self):
        return self.win_title

    def get_graph(self):
        return self.dag.graph

    def add_nodes(self, *arg: set[ScriptArgs]):
        """添加任务节点"""
        try:
            # 将后续节点添加到集合末尾
            self.nodes.update(*arg)
        except TypeError:
            logger.error(f'不能重复添加节点')
        return self

    def add_edge(self, ind_node: ScriptArgs, dep_node: ScriptArgs):
        """在任务节点添加边 因为底层数据结构采用dag,所有只能往下运行"""
        try:
            if ind_node in self.nodes and dep_node in self.nodes:
                edge = Edge(ind_node, dep_node)
                if edge not in self.edges:
                    self.edges.add(edge)
            else:
                logger.warning(f"添加关系时，{ind_node}或{dep_node}节点不存在")
        except TypeError as t:
            logger.error(f"键重复，{t}")
        except Exception as e:
            logger.error(f"{log.detail_error()}")
        return self

    def add_edges(self, *arg):
        """在任务节点添加边 因为底层数据结构采用dag,所有只能往下运行"""
        try:

            self.edges.update(*arg)
        except TypeError as t:
            logger.error(f"键重复，{t}")
        except Exception as e:
            logger.error(f"{log.detail_error()}")
        return self

    def build(self):
        self.sort()
        for node in self.nodes:
            self.dag.add_node(node)
        for edge in self.edges:
            try:
                self.dag.add_edge(*edge)
            except Exception as e:
                logger.error(f"{log.detail_error()}")

    def sort(self):
        self.nodes = sorted(self.nodes, key=lambda ScriptArgs: ScriptArgs.weight)

    def delete_edge(self, ind_node, dep_node):
        """删除边"""
        try:
            self.dag.delete_edge(ind_node, dep_node)
        except KeyError:
            logger.error(f'图形中不存此边')
        return self

    def delete_node(self, node_name):
        """删除节点，会将边一起删除"""
        try:
            self.dag.delete_node(node_name)
        except KeyError:
            logger.error(f'图形中不存此节点')
        return self

    def show_dag(self):
        """显示流程节点，以及它可达节点"""
        try:
            return self.dag.topological_sort()
        except ValueError:
            logger.error(f'不允许有环流程不正确')

    def get_head(self):
        return self.nodes[0]


# ===========================================================


now = lambda: t.time()


class Execute(object):
    """运行构建器构建的参数"""

    def __init__(self, retry_time, retry_count, task_loop, monitor):
        # 任务循环次数
        self.retry_time = retry_time
        self.retry_count = retry_count
        self.task_loop = task_loop
        self.monitor = monitor
        self.pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix='')

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
        simulate.do_screenshot(screenshot_path, region)
        return cv.imread(screenshot_path)

    def init_screenshot(self, win_title: str):
        """截图预热"""
        screenshot_name = "screenshot" + generate_random_string(4)
        # 进行区域处理
        region = simulate.get_region_by_title(win_title)
        screenshot_path = f"./imgs/screenshot/{screenshot_name}.png"
        return region, screenshot_path

    # TODO 将这个执行转化成类 用来方便参数传递 
    def execute_task_args(self, task: BuildTaskArgs):
        region = simulate.get_region_by_title(task.win_title)
        match self.monitor:
            case "screen":
                # 不开启视频流监控 采用截图方式 响应相对较慢
                self.screen_execute(task)
                # TODO 在BuildTaskArgs 加入 task_loop 属性
                ScreenExecute(region=region, task_loop=task.task_loop, task_args=task).execute()
            case "video":
                # 视频流监控
                self.video_execute(task)
                pass

    def video_execute(self, task):
        pass


# 得到中点坐标
def get_xy(strategy: Strategy.ClickStrategy, min_loc, box):
    _strategy = strategy.policy
    point = POINT()
    match _strategy:
        case Policy.CENTER:
            res = get_cent_xy(min_loc, box)
            point = POINT(x=res.x, y=res.y)
        case Policy.RANDOM:
            res = get_random_xy(min_loc, box)
            point = POINT(x=res.x, y=res.y)
        case Policy.WITHOUT:
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


def generate_random_string(length=8):
    import random
    import string
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


def run(build: [Build], script_tasks: list[BuildTaskArgs]):
    processor = init_execute_processor()
    tasks = []
    if GUARD:
        for title in build.win_titles:
            POOL.submit(simulate.keep_visible_win, title)

    for script_tasks in script_tasks:
        task = POOL.submit(processor.execute_task_args, script_tasks)
        tasks.append(task)
        t.sleep(1)
    wait(tasks)


class ScreenExecute(object):
    def __init__(self, region, task_loop, task_args):
        self.mss = mss.mss()  # 截图
        self.region = region  # 监视区域
        self.retry_time = RETRYTIME  # 重试时间
        self.task_loop = task_loop  # 循环次数
        self.task_args = task_args  # 运行参数
        self.retry_count = RETRYCOUNT

    def execute(self):
        dag = self.task_args.dag
        # 双端队列 插入在队尾
        q = deque()

        q.append(dag.ind_nodes())
        while q.__len__() != 0:
            nodes = q.pop()
            start_time = now()
            # TODO进行拆分
            flag = False
            while now() - start_time < self.retry_time:
                scrreenshot = np.array(self.mss.grab(self.region))
                self.do_execute(q=q, nodes=nodes, screenshot=scrreenshot)

    def do_execute(self, q, nodes: list[ScriptArgs], screenshot):
        # 批量处理
        for node in nodes:

            try:
                box, min_loc = self.execute_match_rule(match_rule=node.match_rule, screenshot=screenshot)  # 匹配
                self.execute_strategy(strategy=node.strategy, box=box, min_loc=min_loc)  # 匹配之后
                # TODO 进行是否点击校验
                self.is_click(node.match_rule)
            except exception.NOT_FIND_EXCEPTION as e:
                logger.warning(e)
                t.sleep(1)
                continue
            except exception.NOT_CLICK_EXCEPTION as e:
                logger.warning(f"{e},retry")
                # TODO重试
                count = 0
                self.retry(match_rule=node.match_rule, strategy=node.strategy, count=count)
                continue
            except Exception as e:
                logger.error(f"😭😭😭{log.detail_error()}")
                continue
            down = self.task_args.dag.downstream(node)
            if len(down) != 0:
                q.append(down)

        else:
            # Max retries exceeded, raise an exception or handle it as needed
            logger.warning(f"🙃🙃🙃{self.retry_time}秒点击失败：{str(node)}")

    def retry(self, match_rule, strategy, count):
        if count > self.retry_count:
            return
        try:
            box, min_loc = self.execute_match_rule(match_rule=match_rule,
                                                   screenshot=np.array(self.mss.grab(self.region)))
            self.execute_strategy(strategy=strategy, box=box, min_loc=min_loc)
            self.is_click(match_rule=match_rule)
        except exception.NOT_FIND_EXCEPTION as e:
            # 表示没有找到 不在进行重试
            return
        except exception.NOT_CLICK_EXCEPTION as e:
            count += 1
            self.retry(match_rule=match_rule, strategy=strategy, count=count)

    def execute_match_rule(self, match_rule, screenshot):

        match type(match_rule):
            case MatchRule.Template:
                """模板匹配"""

                template = cv.cache_imread(f"./imgs/{match_rule.template_name}.png")

                threshold, min_loc = cv.do_match(screenshot, template)
                if threshold > match_rule.threshold:
                    # 匹配成功
                    height, width = template.shape[:2]
                    return BOX(height=height, width=width), min_loc
                else:
                    # 匹配失败 retry
                    raise exception.NOT_FIND_EXCEPTION(f"😐😐😐没有匹配{match_rule.template_name},retry")
            case MatchRule.Ocr:
                # Ocr
                pass
                """ocr"""

    def execute_strategy(self, strategy, min_loc, box):
        match type(strategy):
            case Strategy.ClickStrategy:
                point = get_xy(strategy, min_loc, box)
                simulate.click(point, strategy.button.value)

            case Strategy.InputKeyStrategy:
                simulate.send_keys()

    def is_click(self, match_rule):
        try:
            self.execute_match_rule(match_rule=match_rule, screenshot=np.array(self.mss.grab(self.region)))
        except exception.NOT_FIND_EXCEPTION as e:
            # 表示已经点击
            return True

        raise exception.NOT_CLICK_EXCEPTION(f"😐😐😐没有点击{match_rule.template_name}")
