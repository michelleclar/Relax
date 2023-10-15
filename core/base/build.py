from ctypes import Union, c_char_p, c_int
from enum import Enum
from core.struct import dag
import log

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
        def __init__(self, template_name):
            self.template_name = template_name

        def __str__(self):
            return f'Template(template_name={self.template_name})'


class ClickStrategy(Enum):
    """点击策略"""
    # CLICK_CENTER_MATCH_POSITION = 1
    # CLICK_RANDOM_MATCH_POSITION = 2
    # CLICK_WITHOUT_MATCH_POSITION = 3
    CENTER = 1
    RANDOM = 2
    WITHOUT = 3


class InputKeyStrategy(Enum):
    """点击策略"""
    CLICK_CENTER_MATCH_POSITION = 'click_center_match_position'
    CLICK_RANDOM_MATCH_POSITION = 'click_random_match_position'
    CLICK_WITHOUT_MATCH_POSITION = 'click_without_match_position'


class TaskStrategy(Union):
    _fields_ = [
        ("click", c_int),
        ("input_key", c_char_p)
    ]


class ScriptArgs(object):
    def __init__(self, task_name: any, strategy: [InputKeyStrategy, ClickStrategy],
                 match_rule: [MatchRule.Ocr, MatchRule.Template]):
        self.task_name = task_name
        self.match_rule = match_rule
        self.strategy = strategy

    def __eq__(self, other):
        if not isinstance(other, ScriptArgs):
            return False
        return self.task_name == other.task_name

    def __hash__(self):
        return hash(self.task_name)

    def __str__(self):
        return f'ScriptArgs(task_name={self.task_name}, match_rule={self.match_rule}, strategy={self.strategy})'


class Build(object):
    class BuildTaskArgs(object):

        def __init__(self):
            self.dag = dag.DAG()

        def add_node(self, arg):
            try:
                self.dag.add_node(arg)
            except KeyError:
                logger.error(f'不能重复添加节点')
            return self

        def add_edge(self, ind_node, dep_node):
            try:
                self.dag.add_edge(ind_node, dep_node)
            except KeyError:
                logger.error(f'图形中不存在一个或多个节点')
            except Exception:
                logger.error(f'{log.detail_error()}')
            return self

        def delete_edge(self, ind_node, dep_node):
            try:
                self.dag.delete_edge(ind_node, dep_node)
            except KeyError:
                logger.error(f'图形中不存此边')
            return self

        def delete_node(self, node_name):
            try:
                self.dag.delete_node(node_name)
            except KeyError:
                logger.error(f'图形中不存此节点')
            return self

        def show_dag(self):
            try:
                return self.dag.topological_sort()
            except ValueError:
                logger.error(f'流程不正确')


def main():
    a1 = ScriptArgs("开始", ClickStrategy.CENTER, MatchRule().template("action"))
    a2 = ScriptArgs("失败", ClickStrategy.CENTER, MatchRule().template("failed"))

    a3 = ScriptArgs("结算", ClickStrategy.CENTER, MatchRule().template("settle"))
    a4 = ScriptArgs("结束", ClickStrategy.CENTER, MatchRule().template("end"))
    task = Build().BuildTaskArgs()
    _dag = (task.add_node(a1).add_node(a2).add_node(a3).add_node(a4)
            .add_edge(a1, a2).add_edge(a1, a3).add_edge(a3, a4))
    print(_dag.show_dag())


if __name__ == '__main__':
    main()
