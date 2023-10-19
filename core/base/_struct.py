from collections import OrderedDict, defaultdict
from copy import copy, deepcopy
from ctypes import Union, c_char_p, c_int, c_long, Structure
"""
orderedDict 可以记住键的插入顺序的字典 （map + linked）
"""
class DAG(object):
    """
    有向无环图实现。
    """

    def __init__(self):
        """
        构造没有节点或边的新 DAG。
        """
        self.reset_graph()

    def add_node(self, node_name, graph=None):
        """
        如果节点尚不存在，请添加节点，否则出错。
        """
        if not graph:
            graph = self.graph
        if node_name in graph:
            raise KeyError('node %s already exists' % node_name)
        graph[node_name] = set()

    def add_node_if_not_exists(self, node_name, graph=None):
        """
        对外提供的添加接口
        """
        try:
            self.add_node(node_name, graph=graph)
        except KeyError:
            pass

    def delete_node(self, node_name, graph=None):
        """
        Deletes this node and all edges referencing it.
        删除此节点和引用它的所有边
        """
        if not graph:
            graph = self.graph
        if node_name not in graph:
            raise KeyError('node %s does not exist' % node_name)
        graph.pop(node_name)

        for node, edges in graph.items():
            if node_name in edges:
                edges.remove(node_name)

    def delete_node_if_exists(self, node_name, graph=None):
        """
        对外提供的删除接口
        """
        try:
            self.delete_node(node_name, graph=graph)
        except KeyError:
            pass

    def add_edge(self, ind_node, dep_node, graph=None):
        """
        在指定节点之间添加边（依赖项）。
        """
        if not graph:
            graph = self.graph
        if ind_node not in graph or dep_node not in graph:
            raise KeyError('one or more nodes do not exist in graph')
        # 深度拷贝
        test_graph = deepcopy(graph)
        test_graph[ind_node].add(dep_node)
        is_valid, message = self.validate(test_graph)
        if is_valid:
            graph[ind_node].add(dep_node)
        else:
            raise Exception()

    def delete_edge(self, ind_node, dep_node, graph=None):
        """
        从图形中删除边
        """
        if not graph:
            graph = self.graph
        if dep_node not in graph.get(ind_node, []):
            raise KeyError('this edge does not exist in graph')
        graph[ind_node].remove(dep_node)

    def rename_edges(self, old_task_name, new_task_name, graph=None):
        """
        更改对现有边中任务的引用。
        """
        if not graph:
            graph = self.graph
        for node, edges in graph.items():

            if node == old_task_name:
                graph[new_task_name] = copy(edges)
                del graph[old_task_name]

            else:
                if old_task_name in edges:
                    edges.remove(old_task_name)
                    edges.add(new_task_name)

    def predecessors(self, node, graph=None):
        """
        返回给定节点的所有前置任务的列表
        """
        if graph is None:
            graph = self.graph
        return [key for key in graph if node in graph[key]]

    def downstream(self, node, graph=None):
        """
        返回此节点具有边缘的所有节点的列表。
        """
        if graph is None:
            graph = self.graph
        if node not in graph:
            raise KeyError('node %s is not in graph' % node)
        return list(graph[node])

    def all_downstreams(self, node, graph=None):
        """
        按拓扑顺序返回依赖项图中给定节点下游的所有节点的列表。
        """
        if graph is None:
            graph = self.graph
        nodes = [node]
        nodes_seen = set()
        i = 0
        while i < len(nodes):
            downstreams = self.downstream(nodes[i], graph)
            for downstream_node in downstreams:
                if downstream_node not in nodes_seen:
                    nodes_seen.add(downstream_node)
                    nodes.append(downstream_node)
            i += 1
        return list(
            filter(
                lambda node: node in nodes_seen,
                self.topological_sort(graph=graph)
            )
        )

    def all_leaves(self, graph=None):
        """
        返回所有叶子（没有下游的节点）的列表
        """
        if graph is None:
            graph = self.graph
        return [key for key in graph if not graph[key]]

    def from_dict(self, graph_dict):
        """
        重置图形并从传递的字典构建它。字典采用 {node_name： [定向边缘]} 的形式
        """

        self.reset_graph()
        for new_node in graph_dict.keys():
            self.add_node(new_node)
        for ind_node, dep_nodes in graph_dict.items():
            if not isinstance(dep_nodes, list):
                raise TypeError('dict values must be lists')
            for dep_node in dep_nodes:
                self.add_edge(ind_node, dep_node)

    def reset_graph(self):
        """
        将图形还原为空状态
        创建一个map
        记录所有节点
        节点表
        """
        self.graph = OrderedDict()

    def ind_nodes(self, graph=None):
        """
        返回图形中没有依赖项的所有节点的列表。
        """
        if graph is None:
            graph = self.graph
        # 将遍历图中节点
        dependent_nodes = set(
            node for dependents in graph.values() for node in dependents
        )
        return [node for node in graph.keys() if node not in dependent_nodes]

    def validate(self, graph=None):
        """
        返回 DAG 是否有效的（布尔值、消息）
        """
        graph = graph if graph is not None else self.graph
        if len(self.ind_nodes(graph)) == 0:
            return False, 'no independent nodes detected'
        try:
            self.topological_sort(graph)
        except ValueError:
            return False, 'failed topological sort'
        return True, 'valid'

    def topological_sort(self, graph=None):
        """
        返回 DAG 的拓扑顺序。如果无法做到这一点（图形无效），则会引发错误。
        """
        if graph is None:
            graph = self.graph
        result = []
        in_degree = defaultdict(lambda: 0)

        for u in graph:
            for v in graph[u]:
                in_degree[v] += 1
        ready = [node for node in graph if not in_degree[node]]

        while ready:
            u = ready.pop()
            result.append(f'{str(u)}')
            for v in graph[u]:
                in_degree[v] -= 1
                if in_degree[v] == 0:
                    ready.append(v)

        if len(result) == len(graph):
            return result
        else:
            raise ValueError('graph is not acyclic')

    def size(self):
        return len(self.graph)

    def __repr__(self):
        return f"DAG(nodes={self.graph.keys()})"

    def get_node(self, node_name):
        """
        按名称获取节点。
        """
        return self.graph.get(node_name)

    def copy(self):
        """
        创建 DAG 的副本。
        """
        new_dag = DAG()
        new_dag.graph = deepcopy(self.graph)
        return new_dag
    
class Offset(Structure):
    _fields_ = [("up", c_long),
                ("down", c_long),
                ("right",c_long),
                ("left",c_long)]
    
class POINT(Structure):
    _fields_ = [("x", ctypes.c_long),
                ("y", ctypes.c_long)]

