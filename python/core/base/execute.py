import time as t
from collections import deque
from concurrent.futures import ThreadPoolExecutor, wait
from enum import Enum

import mss
import numpy as np

from python.commons import exception
from python.commons.utils.format import DataFormat
from python.core.base import simulate
from python.core.base import cv, log
from python.core.base.structs import POINT, BOX

# 执行方法
logger = log.get_logger()

# 重试时间
RETRYTIME = 10
# 疑似点击失败 重试次数
RETRYCOUNT = 3
# 监控
MONITOR = None

DEBUG = False

GUARD = False
POOL = ThreadPoolExecutor(max_workers=10)


class asyn_queue(object):

    def __init__(self):
        # TODO 目前没有采用官方线程安全的队列 需测试是否需要替换 如果不需要将 将使用c++重写此队列
        self.img_queue = deque()  # 对外提供的队列
        self.point_queue = deque()  # 统计点击点
        self.mss = mss.mss()  # 截图

    def push_img(self, path, img):
        """

        :param path:
        :param img:
        """
        self.img_queue.append((path, img))

    def push_point(self, policy, point):
        self.point_queue.append((policy, point))

    def execute_point(self):

        while True:
            io_center = open('./point/center', 'a')
            io_random = open('./point/random', 'a')
            io_without = open('./point/without', 'a')
            while len(self.point_queue) != 0:
                e = self.point_queue.pop()
                policy = e[0]
                point = e[1]
                match policy:
                    case Policy.CENTER:
                        io_center.write(f'{point.x},{point.y} ')
                    case Policy.RANDOM:
                        io_random.write(f'{point.x},{point.y} ')

    def execute_img(self):
        while True:
            while len(self.img_queue) != 0:
                e = self.img_queue.pop()
                path = e[0]
                img = e[1]
                cv.save_img(path=path, img=img)

    def run(self):
        while True:
            while len(self.img_queue) != 0:
                e = self.img_queue.pop()
                path = e[0]
                img = e[1]
                cv.save_img(path=path, img=img)


Asyn = asyn_queue()
POOL.submit(Asyn.execute_point)
POOL.submit(Asyn.execute_img)

def init_execute_processor():
    """

    :return:
    """
    from yaml import load, Loader
    logger.info("正在读取配置")
    with open("config.yml", "r", encoding='utf-8') as f:
        # 重试时间
        global RETRYTIME
        # 疑似点击失败 重试次数
        global RETRYCOUNT
        # 监控
        global MONITOR

        global DEBUG

        global GUARD
        ayml = load(f.read(), Loader=Loader)
        execute_consts = ayml["execute"]

        RETRYTIME = execute_consts['RetryTime']
        RETRYCOUNT = execute_consts['RetryCount']
        MONITOR = execute_consts['Monitor']

        switch_consts = ayml["switch"]
        DEBUG = switch_consts["Debug"]
        GUARD = switch_consts["Guard"]
    logger.info(f'配置内容为{ayml}')

    return Execute(retry_time=RETRYTIME, retry_count=RETRYCOUNT, monitor=MONITOR)


# ===========================================================


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
        """

        :param text:
        :return:
        """
        return self.Ocr(text=text)

    def template(self, template_name):
        """

        :param template_name:
        :return:
        """
        return self.Template(template_name=template_name)

    class Ocr(object):
        """

        """

        def __init__(self, text):
            self.text = text

        def __str__(self):
            return f'Ocr(text={self.text})'

    class Template(object):
        """

        """

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
        from python.core.base.structs import OFFSET
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
        self.is_match = False
        self.fail_count = 0  # 失败次数
        self.time = -1  # 上一步到此步骤的时间
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
    """

    """

    def __init__(self):
        self.win_titles = set()
        pass

    def BuildTaskArgs(self, win_title: str, task_loop: int):
        """

        :param win_title:
        :param task_loop:
        :return:
        """
        self.win_titles.add(win_title)
        return BuildTaskArgs(win_title=win_title, task_loop=task_loop)


class BuildTaskArgs(object):
    """任务流构建器"""

    def __init__(self, win_title: str, task_loop: int):
        from python.core.base.structs import DAG
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
                edge = (ind_node, dep_node)
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


# ===========================================================


now = lambda: t.time()


class Execute(object):
    """运行构建器构建的参数"""

    def __init__(self, retry_time, retry_count, monitor):
        # 任务循环次数
        self.retry_time = retry_time
        self.retry_count = retry_count
        self.monitor = monitor
        self.pool = ThreadPoolExecutor(max_workers=10, thread_name_prefix='')

    def execute(self, task: [Build.BuildTaskArgs]):
        """

        :param task:
        """
        task_type = type(task)
        match task_type:
            case Build.BuildTaskArgs:
                self.execute_task_args(task)
            case _:
                logger.error(f'不支持此类型：{task_type}')

    def execute_task_args(self, task: BuildTaskArgs):
        """

        :param task:
        """
        region = simulate.get_region_by_title(task.win_title)
        match self.monitor:
            case "screen":
                # 不开启视频流监控 采用截图方式 响应相对较慢
                ScreenExecute(region=region, task_loop=task.task_loop, task_args=task).execute()
            case "video":
                # 视频流监控
                VideoExecute(region=region, task_loop=task.task_loop, task_args=task).execute()


# 得到中点坐标
def get_xy(strategy: Strategy.ClickStrategy, pt, box):
    """

    :param strategy:
    :param pt:
    :param box:
    :return:
    """
    _strategy = strategy.policy
    point = POINT()
    match _strategy:
        case Policy.CENTER:
            res = get_cent_xy(pt, box)
            point = POINT(x=res.x, y=res.y)
            Asyn.point_queue.append((Policy.CENTER, point))
        case Policy.RANDOM:
            res = get_random_xy(pt, box)
            point = POINT(x=res.x, y=res.y)
            Asyn.point_queue.append((Policy.RANDOM, point))
        case Policy.WITHOUT:
            # 匹配之外的点
            pass
    point.x += strategy.offset.x
    point.y += strategy.offset.y

    return point


def send_keys():
    """

    """
    pass


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


def get_random_xy(avg, box):
    """

    :param avg:
    :param box:
    :return:
    """
    import random
    height, width = box
    x, y = avg
    x += random.uniform(0, height)
    y += random.uniform(0, width)
    return POINT(x=x, y=y)


def generate_random_string(length=8):
    """

    :param length:
    :return:
    """
    import random
    import string
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


def generate_current_time_name():
    """

    :return:
    """
    return t.strftime(DataFormat.ONLY_TIME.value, t.localtime())


def run(build: [Build], script_tasks: list[BuildTaskArgs]):
    """

    :param build:
    :param script_tasks:
    """
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
    """

    """

    def __init__(self, region, task_loop, task_args: BuildTaskArgs):

        self.mss = mss.mss()  # 截图
        self.region = region  # 监视区域
        self.retry_time = RETRYTIME  # 重试时间
        self.task_loop = task_loop  # 循环次数
        self.task_args = task_args  # 运行参数
        self.cycle = len(task_args.nodes) * RETRYTIME  # 用来进行筛选
        self.retry_count = RETRYCOUNT

    def screenshot(self):
        """

        :return:
        """
        img = np.array(self.mss.grab(self.region))
        cv.cvtColor(img)
        return cv.cvtColor(img)

    def execute(self):
        """

        """
        dag = self.task_args.dag
        # 双端队列 插入在队尾
        q = deque()
        q.append(dag.ind_nodes())
        # TODO任务开始选择一个符号用于日志观察
        logger.info(f'监视{self.task_args.win_title}任务开始')
        while q.__len__() != 0:
            nodes = q.pop()
            self.do_execute(q=q, nodes=nodes)

    def do_execute(self, q, nodes: list[ScriptArgs]):
        """

        :param q:
        :param nodes:
        :return:
        """
        # 批量处理
        if self.cycle == 0:
            return

        flag = False
        for i in range(self.task_loop):
            start_time = now()
            while now() - start_time < self.cycle:
                for node in nodes:
                    img = self.screenshot()
                    try:
                        box, pt = self.execute_match_rule(match_rule=node.match_rule, screenshot=img)  # 匹配
                        self.execute_strategy(strategy=node.strategy, box=box, min_loc=pt)  # 匹配之后
                        self.is_click(node.match_rule)
                        flag = True
                    except exception.NOT_MATCH_EXCEPTION as e:
                        logger.warning(f'{e},当前置性度:{node.match_rule.threshold}')
                        t.sleep(1)
                        continue
                    except exception.CLICK_EXCEPTION as e:
                        path = f'./imgs/not_click/{generate_current_time_name()}.png'
                        Asyn.push_img(path=path, img=img)
                        logger.warning(f"{e},retry,path：{path}")
                        self.retry(match_rule=node.match_rule, strategy=node.strategy, count=0)
                        continue
                    except Exception as e:
                        # 未知力量影响将图片进行保存
                        path = f'./imgs/unknown/{generate_current_time_name()}.png'
                        logger.warning(f"😭😭😭{log.detail_error()},path:{path}")
                        Asyn.push_img(path=path, img=img)
                        continue
                    down = self.task_args.dag.downstream(node)
                    if len(down) != 0:
                        q.append(down)
                    break
                if flag:
                    flag = False
                    break
            else:
                # 全屏进行截图
                path = f'./imgs/cycle/{generate_current_time_name()}.png'
                self.mss.shot(mon=-1, output=path)
                logger.warning(f"🙃🙃🙃{self.cycle}秒没有匹配到任何目标，{[str(x) for x in nodes]}")

    def retry(self, match_rule, strategy, count):
        """

        :param match_rule:
        :param strategy:
        :param count:
        :return:
        """
        if count > self.retry_count:
            logger.warning(f'重试次数已经达到{self.retry_count}')
            return
        img = self.screenshot()
        try:
            box, min_loc = self.execute_match_rule(match_rule=match_rule,
                                                   screenshot=img)
            self.execute_strategy(strategy=strategy, box=box, min_loc=min_loc)
            self.is_click(match_rule=match_rule)
        except exception.NOT_MATCH_EXCEPTION as e:
            # 表示没有找到 不在进行重试
            path = f'./imgs/not_click/{generate_current_time_name()}.png'
            logger.warning(f'{e},path:{path}')
            Asyn.push_img(path=path, img=img)
            return
        except exception.CLICK_EXCEPTION as e:
            count += 1
            path = f'./imgs/not_click/{generate_current_time_name()}.png'
            logger.warning(f'重试次数{count},path:{path}')
            Asyn.push_img(path=path, img=img)
            self.retry(match_rule=match_rule, strategy=strategy, count=count)

    def execute_match_rule(self, match_rule, screenshot):
        """

        :param match_rule:
        :param screenshot:
        :return:
        """
        match type(match_rule):
            case MatchRule.Template:
                """模板匹配"""

                template = cv.cache_imread(f"./imgs/{match_rule.template_name}.png")

                threshold, pt = cv.do_match(screenshot, template)
                if threshold > match_rule.threshold:
                    # 匹配成功
                    height, width = template.shape[:2]
                    box = BOX(height=height, width=width)
                    cv.rectangle(target=screenshot, pt=pt, box=box)
                    if DEBUG:
                        show(f"{self.task_args.win_title}+{match_rule.template_name}",screenshot)
                    return box, pt
                else:
                    # 匹配失败 retry
                    raise exception.NOT_MATCH_EXCEPTION(f"😐😐😐没有匹配{match_rule.template_name},retry")
            case MatchRule.Ocr:
                # Ocr
                pass
                """ocr"""

    def execute_strategy(self, strategy, min_loc, box):
        """

        :param strategy:
        :param min_loc:
        :param box:
        """
        match type(strategy):
            case Strategy.ClickStrategy:
                point = get_xy(strategy, min_loc, box)
                point.x += self.region[0]
                point.y += self.region[1]
                simulate.click(point, strategy.button.value)
                logger.info(f'🖱️🖱️🖱️点击坐标：偏移后：{point}，偏移量：{strategy.offset}')
            case Strategy.InputKeyStrategy:
                simulate.send_keys()
                # 输入按键
                logger.info(f'')

    def is_click(self, match_rule):
        """

        :param match_rule:
        :return:
        """
        try:
            self.execute_match_rule(match_rule=match_rule, screenshot=self.screenshot())
        except exception.NOT_MATCH_EXCEPTION as e:
            return True

        raise exception.CLICK_EXCEPTION(f"😐😐😐没有点击{match_rule.template_name}")


class VideoExecute(object):
    """

    """

    def __init__(self, region, task_loop: int, task_args: BuildTaskArgs):
        self.mss = mss.mss()  # 截图
        self.region = region  # 监视区域
        self.retry_time = RETRYTIME  # 重试时间
        self.task_loop = task_loop  # 循环次数
        self.task_args = task_args  # 运行参数
        self.retry_count = RETRYCOUNT  # 重试次数
        self.cycle = len(task_args.nodes) * RETRYTIME  # 用来进行筛选

    def screenshot(self):
        """

        :return:
        """
        img = np.array(self.mss.grab(self.region))
        cv.cvtColor(img)
        return cv.cvtColor(img)

    def execute(self):
        """

        """
        nodes = self.task_args.nodes
        logger.info(f'监视{self.task_args.win_title}任务开始,运作参数{[str(x) for x in nodes]}')
        self.do_execute(nodes)

    def do_execute(self, nodes: set[ScriptArgs]):
        """

        :param nodes:
        :return:
        """
        # 批量处理
        if self.cycle == 0:
            return
        new_nodes = self.filter_nodes(nodes)
        length = len(new_nodes)
        count = 0
        for i in range(self.task_loop):
            temp = set()
            start = now()
            self.execute_nodes(nodes=nodes)
            if length != len(temp):
                count += 1
                # 全屏进行截图
                path = f'./imgs/cycle/{generate_current_time_name()}.png'
                self.mss.shot(mon=-1, output=path)
                logger.warning(f'{now() - start}时间内没有匹配任何目标,path:{path}')
            if count > 10:
                new_nodes = self.filter_nodes(new_nodes)
                length = len(new_nodes)

    def filter_nodes(self, nodes: set[ScriptArgs]):
        """

        :param nodes:
        :return:
        """
        start_time = now()
        while now() - start_time < self.cycle:
            self.execute_nodes(nodes=nodes)
        return set(filter(lambda x: x.fail_count >= 0, nodes))

    def execute_nodes(self, nodes: set[ScriptArgs]):
        """

        :param nodes:
        """
        for node in nodes:
            img = self.screenshot()
            if DEBUG:
                show(self.task_args.win_title,img)
            try:
                box, min_loc = self.execute_match_rule(match_rule=node.match_rule,
                                                       screenshot=img)  # 匹配
                if DEBUG:
                    show(self.task_args.win_title,img)
                self.execute_strategy(strategy=node.strategy, box=box, min_loc=min_loc)  # 匹配之后
                self.is_click(node.match_rule)
                node.fail_count -= 1
            except exception.NOT_MATCH_EXCEPTION as e:
                logger.warning(f'{e},当前置性度:{node.match_rule.threshold}')
                continue
            except exception.CLICK_EXCEPTION as e:
                # 未知力量影响 将图片进行保存
                path = f'./imgs/not_click/{generate_current_time_name()}.png'
                Asyn.push_img(path=path, img=img)
                logger.warning(f"{e},retry,path：{path}")
                self.retry(match_rule=node.match_rule, strategy=node.strategy, count=0)
                continue
            except Exception as e:
                # 未知力量影响将图片进行保存
                path = f'./imgs/unknown/{generate_current_time_name()}.png'
                logger.warning(f"😭😭😭{log.detail_error()},path:{path}")
                Asyn.push_img(path=path, img=img)
                continue

    def retry(self, match_rule, strategy, count):
        """

        :param match_rule:
        :param strategy:
        :param count:
        :return:
        """
        if count > self.retry_count:
            logger.warning(f'重试次数已经达到{self.retry_count}')
            return
        img = self.screenshot()
        try:
            box, min_loc = self.execute_match_rule(match_rule=match_rule,
                                                   screenshot=img)
            self.execute_strategy(strategy=strategy, box=box, min_loc=min_loc)
            self.is_click(match_rule=match_rule)
        except exception.NOT_MATCH_EXCEPTION as e:
            # 表示没有找到 不在进行重试
            path = f'./imgs/not_click/{generate_current_time_name()}.png'
            logger.warning(f'{e}')
            Asyn.push_img(path=path, img=img)
            return
        except exception.CLICK_EXCEPTION as e:
            count += 1
            path = f'./imgs/not_click/{generate_current_time_name()}.png'
            logger.warning(f'重试次数{count},path:{path}')
            Asyn.push_img(path=path, img=img)
            self.retry(match_rule=match_rule, strategy=strategy, count=count)

    def execute_match_rule(self, match_rule, screenshot):
        """

        :param match_rule:
        :param screenshot:
        :return:
        """
        match type(match_rule):
            case MatchRule.Template:
                """模板匹配"""

                template = cv.cache_imread(f"./imgs/{match_rule.template_name}.png")

                threshold, min_loc = cv.do_match(screenshot, template)

                if threshold > match_rule.threshold:
                    # 匹配成功
                    height, width = template.shape[:2]
                    box = BOX(height=height, width=width)
                    cv.rectangle(target=screenshot, pt=min_loc, box=box)
                    return box, min_loc
                else:
                    # 匹配失败 retry
                    raise exception.NOT_MATCH_EXCEPTION(f"😐😐😐没有匹配{match_rule.template_name}")
            case MatchRule.Ocr:
                # Ocr
                pass
                """ocr"""

    def execute_strategy(self, strategy, min_loc, box):
        """

        :param strategy:
        :param min_loc:
        :param box:
        """
        match type(strategy):
            case Strategy.ClickStrategy:
                point = get_xy(strategy, min_loc, box)
                point.x += self.region[0]
                point.y += self.region[1]
                simulate.click(point, strategy.button.value)
                logger.info(f'🖱️🖱️🖱️点击坐标：偏移后：{point}，偏移量：{strategy.offset}')
            case Strategy.InputKeyStrategy:
                simulate.send_keys()
                logger.info(f'')

    def is_click(self, match_rule):
        """

        :param match_rule:
        :return:
        """
        img = self.screenshot()
        try:
            self.execute_match_rule(match_rule=match_rule, screenshot=img)
        except exception.NOT_MATCH_EXCEPTION as e:
            return True
        raise exception.CLICK_EXCEPTION(f"😐😐😐疑似没有点击{match_rule.template_name},retry")
def show(title: str,img):
    cv.show(title, img)
