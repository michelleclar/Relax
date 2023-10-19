import log
from enum import Enum
from type import DAG,OFFSET,POINT
from collections import namedtuple

Edge = namedtuple('Edge', ['ind_node', 'dep_node'])

logger = log.get_logger()


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

    class Ocr(object):
        def __init__(self, text):
            self.text = text

        def __str__(self):
            return f'Ocr(text={self.text})'

    def template(self, template_name):
        return self.Template(template_name=template_name)

    class Template(object):
        def __init__(self, template_name, threshold=None):
            self.template_name = template_name
            self.threshold = threshold if threshold is not None else 0.9

        def __str__(self):
            return f'Template(template_name={self.template_name})'


class Strategy(Enum):
    CENTER = 1  # 点击匹配的图像中心
    RANDOM = 2  # 在匹配区域最近点击
    WITHOUT = 3  # 点击匹配区域之外的地方

class Button(Enum):
    LEFT = "left"
    MIDDLE = "middle"
    RIGHT = "right"
    PRIMARY = "primary"
    SECONDARY = "secondary"
class ClickStrategy(object):
    """点击策略"""
    def __init__(self, strategy: Strategy, offset: OFFSET,button=Button.LEFT):
        self.strategy = strategy
        self.offset = offset
        self.button = button


class InputKeyStrategy(Enum):
    """按键操作策略"""
    CLICK_CENTER_MATCH_POSITION = 'click_center_match_position'
    CLICK_RANDOM_MATCH_POSITION = 'click_random_match_position'
    CLICK_WITHOUT_MATCH_POSITION = 'click_without_match_position'

class ScriptArgs(object):
    """节点参数"""
    _auto_increment_weight = 0

    def __init__(self, task_name: any, strategy: [InputKeyStrategy, ClickStrategy],
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
    """通用构建器"""
    class BuildTaskArgs(object):
        """任务流构建器"""
        def __init__(self, win_title: str):
            self.dag = DAG()
            self.win_title = win_title
            self.nodes = set()
            self.edges = set()

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


def main():
    button = Button.LEFT.value
    print(type(button))
    # a1 = ScriptArgs("开始", ClickStrategy(Strategy.CENTER), MatchRule().template("action"))
    # a2 = ScriptArgs("失败", ClickStrategy(Strategy.CENTER), MatchRule().template("failed"))
    #
    # a3 = ScriptArgs("结算", ClickStrategy(Strategy.CENTER), MatchRule().template("settle"))
    # a4 = ScriptArgs("结束", ClickStrategy(Strategy.CENTER), MatchRule().template("end"))
    # task = Build().BuildTaskArgs("aaa")
    # task.add_nodes({a1, a2, a3, a4})
    # task.add_edge(a1, a2)
    # task.add_edge(a1, a3)
    # task.add_edge(a3, a4)
    # task.build()
    # print(task)


if __name__ == '__main__':
    main()
