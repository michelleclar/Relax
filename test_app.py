import yaml

from core.base.execute import ScriptArgs, Strategy, MatchRule, Button, Policy, Build
from core.base.log import get_logger, detail_error
from core.base.structs import POINT

logger = get_logger()


# 去除dga


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


_nodes = set()
_edge = set()


# def parse_nodes(nodes):
#     heads = defaultdict(list)
#     for node in nodes:
#         a = parse_node(node)
#         if node.get('child'):
#             # 下一步
#             for child in node['child']:
#                 parse_node(child)


#     for head in heads:
#         parse_edge(head)
#     for node in heads:
#         a = parse_node(node)
#         if node.get('child'):
#             # 下一步
#             c = parse_nodes(node['child'])
#             _edge.add((a, c))
#     return a

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
                button = strategy['button']
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


if __name__ == "__main__":
    main()
