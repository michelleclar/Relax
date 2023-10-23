import yaml
from core.base.execute import run, Build, ScriptArgs, Strategy, MatchRule, Policy, Button
import commons.img_name as img_name
from core.base.log import get_logger, detail_error
from core.base.structs import POINT

logger = get_logger()


def main():
    a1 = ScriptArgs(task_name="式神录", strategy=Strategy.ClickStrategy(Policy.CENTER),
                    match_rule=MatchRule().template(img_name.test_1))
    a2 = ScriptArgs(task_name="返回", strategy=Strategy.ClickStrategy(Policy.CENTER),
                    match_rule=MatchRule().template(img_name.test_2))
    #
    # a3 = ScriptArgs(task_name="结算", strategy=ClickStrategy(Strategy.CENTER),
    #                 match_rule=MatchRule().template("settle"))
    # a4 = ScriptArgs(task_name="结束", strategy=ClickStrategy(Strategy.CENTER), match_rule=MatchRule().template("end"))
    build = Build()
    task = build.BuildTaskArgs("主账号")
    task.add_nodes({a1, a2})
    task.add_edge(a1, a2)
    task.build()

    run(build=build, script_tasks=[task])


def main():
    # 加载 YAML 文件
    with open("task.yml", "r") as f:
        args_list = yaml.load(f, Loader=yaml.FullLoader)["tasks"]
    build = Build()
    tasks = []
    # 构建 ScriptArgs 对象
    for args_dict in args_list:
        pool_name = args_dict['task']
        _nodes, _edges = parse(args_dict['nodes'])
        task = build.BuildTaskArgs(pool_name)
        task.add_nodes(_nodes)
        task.add_edges(_edges)
        task.build()
        tasks.append(task)
    print(build, tasks)


def parse(nodes):
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
    node_name = node['node']
    strategy = parse_match_rule(node['match_rule'])
    match_rule = parse_strategy(node['strategy'])
    return ScriptArgs(task_name=node_name, strategy=strategy,
                      match_rule=match_rule)


def parse_strategy(strategy):
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
    match button:
        case 'left':
            return Button.LEFT
        case 'right':
            return Button.RIGHT
        case 'middle':
            return Button.MIDDLE


if __name__ == '__main__':
    main()
