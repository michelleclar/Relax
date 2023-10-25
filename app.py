import yaml
from core.base.execute import run, Build, ScriptArgs, Strategy, MatchRule, Policy, Button
import commons.img_name as img_name
from core.base.log import get_logger, detail_error
from core.base.structs import POINT

logger = get_logger()


def main():
    # 加载 YAML 文件
    with open("task.yml", encoding='utf-8') as f:
        args_list = yaml.load(f, Loader=yaml.FullLoader)["tasks"]
    build = Build()
    tasks = []
    # 构建 ScriptArgs 对象
    for args_dict in args_list:
        pool_name = args_dict['task']
        task_loop = 0
        if args_dict.get('taskloop'):
            task_loop = args_dict['taskloop']
        _nodes, _edges = parse(nodes=args_dict['nodes'])
        task = build.BuildTaskArgs(win_title=pool_name, task_loop=task_loop)
        task.add_nodes(_nodes)
        task.add_edges(_edges)
        task.build()
        tasks.append(task)

    run(build=build, script_tasks=tasks)


def parse(nodes):
    """

    :param nodes:
    :return:
    """
    _nodes = set()
    _edges = set()

    def parse_nodes(nodes):
        for node in nodes:
            a = parse_node(node)
            _nodes.add(a)
            if node.get('child'):
                # 下一步
                for child in node['child']:
                    c = parse_node(child)
                    _edges.add((a, c))
                    parse_nodes([child])

    parse_nodes(nodes)
    return _nodes, _edges


def parse_node(node):
    """

    :param node:
    :return:
    """
    node_name = node['node']
    match_rule = parse_match_rule(node['match_rule'])
    strategy = parse_strategy(node['strategy'])
    return ScriptArgs(task_name=node_name, strategy=strategy,
                      match_rule=match_rule)


def parse_strategy(strategy):
    """

    :param strategy:
    :return:
    """
    res = None
    match strategy['type']:
        case "ClickStrategy":
            policy = Policy.CENTER
            offset = POINT(x=0, y=0)
            button = Button.LEFT
            if strategy.get('policy'):
                policy = strategy['policy']
            if strategy.get('offset'):
                offset = POINT(x=strategy['offset']['x'], y=strategy['offset']['y'])
            if strategy.get('button'):
                button = parse_button(strategy['button'])
            res = Strategy.ClickStrategy(policy=policy, offset=offset, button=button)
        case "InputStrategy":
            key = 'ESC'
            if strategy.get('key'):
                key = strategy['key']
            res = Strategy.InputKeyStrategy(key=key)
    return res


def parse_match_rule(match_rule):
    """

    :param match_rule:
    :return:
    """
    res = None
    match match_rule['type']:
        case "template":
            threshold = 0.9
            value = None
            try:
                value = match_rule['value']
            except Exception as e:
                logger.error(f"{detail_error()}")
                raise e
            if match_rule.get('threshold'):
                threshold = match_rule['threshold']

            res = MatchRule.Template(template_name=value, threshold=threshold)
        case "ocr":
            pass
    return res


def parse_button(button: str):
    """

    :param button:
    :return:
    """
    match button:
        case 'left':
            return Button.LEFT
        case 'right':
            return Button.RIGHT
        case 'middle':
            return Button.MIDDLE


if __name__ == '__main__':
    main()
