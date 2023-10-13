from collections import OrderedDict, defaultdict
from copy import copy, deepcopy

# 构建参数方法

# 任务参数设置  将点击延迟和随机点击迁移到点击事件名中
# 整体参数结构设计
# 匹配规则，ocr匹配:需要有匹配的文字参数 模板匹配:需要模板图片名字
# 点击事件名，点击事件
class TaskFlow:
    self.nextTask:TaskFlows
    
    class Tasks:
    def __init__(self,head):
        """
        head 任务入口 必须
        """
        self.head = head
    
    def setNextTask:
        
    
class Build:
   # 数据结构有向无环图
   # 首节点 模板参数 k：
    def __init__(self):
        self.dga = Dga()
    def add_node(arg):
        try:
            self.dga.add_node(arg) 
        except expression as ex:
 class DAG(object):
    """ Directed acyclic graph implementation. """

    def __init__(self):
        """ Construct a new DAG with no nodes or edges. """
        self.reset_graph()

    def add_node(self, node_name, graph=None):
        """
        Add a node if it does not exist yet, or error out.
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
        """ Deletes this node and all edges referencing it. """
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
        """ Add an edge (dependency) between the specified nodes. """
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
        """ Delete an edge from the graph. """
        if not graph:
            graph = self.graph
        if dep_node not in graph.get(ind_node, []):
            raise KeyError('this edge does not exist in graph')
        graph[ind_node].remove(dep_node)

    def rename_edges(self, old_task_name, new_task_name, graph=None):
        """ Change references to a task in existing edges. """
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
        """ Returns a list of all predecessors of the given node """
        if graph is None:
            graph = self.graph
        return [key for key in graph if node in graph[key]]

    def downstream(self, node, graph=None):
        """ Returns a list of all nodes this node has edges towards. """
        if graph is None:
            graph = self.graph
        if node not in graph:
            raise KeyError('node %s is not in graph' % node)
        return list(graph[node])

    def all_downstreams(self, node, graph=None):
        """Returns a list of all nodes ultimately downstream
        of the given node in the dependency graph, in
        topological order."""
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
        """ Return a list of all leaves (nodes with no downstreams) """
        if graph is None:
            graph = self.graph
        return [key for key in graph if not graph[key]]

    def from_dict(self, graph_dict):
        """ Reset the graph and build it from the passed dictionary.
        The dictionary takes the form of {node_name: [directed edges]}
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
        Restore the graph to an empty state.
        创建一个map
        记录所有节点
        节点表
        """
        self.graph = OrderedDict()

    def ind_nodes(self, graph=None):
        """ Returns a list of all nodes in the graph with no dependencies. """
        if graph is None:
            graph = self.graph
        # 将遍历图中节点 
        dependent_nodes = set(
            node for dependents in graph.values() for node in dependents
        )
        return [node for node in graph.keys() if node not in dependent_nodes]

    def validate(self, graph=None):
        """ Returns (Boolean, message) of whether DAG is valid. """
        graph = graph if graph is not None else self.graph
        if len(self.ind_nodes(graph)) == 0:
            return False, 'no independent nodes detected'
        try:
            self.topological_sort(graph)
        except ValueError:
            return False, 'failed topological sort'
        return True, 'valid'

    def topological_sort(self, graph=None):
        """ Returns a topological ordering of the DAG.
        Raises an error if this is not possible (graph is not valid).
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
            result.append(u)
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


class DAG:
  def __init__(self, vertices):
    self.vertices = vertices
    self.adjacency_list = {}
    for vertex in vertices:
      self.adjacency_list[vertex] = []

  def add_edge(self, u, v):
    self.adjacency_list[u].append(v)

  def is_cyclic(self):
    """
    深度优先搜索，判断图是否有环。

    Args:
      None

    Returns:
      True，如果图有环；False，如果图没有环。
    """

    visited = set()

    def dfs(u):
      visited.add(u)
      for v in self.adjacency_list[u]:
        if v in visited:
          return True
        if dfs(v):
          return True
      return False

    for vertex in self.vertices:
      if vertex in visited:
        continue
      if dfs(vertex):
        return True
    return False


def main():
  vertices = ["A", "B", "C", "D", "E"]
  dag = DAG(vertices)
  dag.add_edge("A", "B")
  dag.add_edge("A", "C")
  dag.add_edge("B", "D")
  dag.add_edge("C", "E")

  print(dag.is_cyclic())

if __name__ == '__main__':
    dag = DAG()
    dag.add_node("a")
    dag.add_node("b")
    dag.add_node("c")
    dag.add_edge("a", "b")
    dag.add_edge("b", "c")
    dag.add_edge("c", "a")
    print(dag.topological_sort())
    print(dag.graph)
    print(dag.all_downstreams("b"))
           
