import pprint
import time
import threading
from commons import const
from core.base.structs import DAG
from collections import deque
from core.base.build import Build, ScriptArgs, MatchRule, ClickStrategy, Strategy
from timeit import timeit
from memory_profiler import profile


def main():
    const.init()
    print(len(const.execute_consts))


def test_dga():
    dag = DAG()
    dag.add_node("A")
    dag.add_node("B")
    dag.add_node("C")
    dag.add_node("D")
    dag.add_node("E")
    dag.add_edge("A", "B")
    dag.add_edge("A", "C")
    dag.add_edge("C", "D")
    print(dag.topological_sort)


def test_deque():
    a1 = ScriptArgs(task_name="开始", strategy=ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("action"))
    a2 = ScriptArgs(task_name="失败", strategy=ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("failed"))

    a3 = ScriptArgs(task_name="结算", strategy=ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("settle"))
    a4 = ScriptArgs(task_name="结束", strategy=ClickStrategy(Strategy.CENTER), match_rule=MatchRule().template("end"))
    task = Build().BuildTaskArgs("aaa")
    task.add_nodes({a1, a2, a3, a4})
    task.add_edge(a1, a2)
    task.add_edge(a1, a3)
    task.add_edge(a3, a4)
    task.build()
    dag = task.dag
    q = deque()
    head = dag.ind_nodes()
    q.append(head)
    while q.__len__() != 0:
        nodes = q.pop()
        # scrreenshot = self.do_screenshot(region=region, screenshot_path=screenshot_path)
        # do_execute(node, screenshot=scrreenshot)
        for node in nodes:
            down = dag.downstream(node)
            if len(down) != 0:
                q.append(down)

def p(arg):
    print(arg)

def test_asyncio():
    import asyncio

    async def hello():
        print("Hello")
        await asyncio.sleep(1)
        print("World")

    async def main():
        await asyncio.gather(hello(), hello(), hello())

    asyncio.run(main())


now = lambda: time.time()


# @profile(precision=4, stream=open(f'../memory_profiler/memory_profiler.log','w+'))
def test_thread():
    for i in range(0, 10):
        run(i)
        start = now()
        thread = threading.Thread(target=run, args=(tuple([i])))
        thread.start()
        print(f"执行时间为{now() - start}")
        while thread.is_alive():
            pass


def run(i):
    import random
    sec = random.uniform(10, 20)
    print(f"休眠：{sec}秒")
    time.sleep(sec)
    return i


def test_thread_poll():
    from concurrent.futures import ThreadPoolExecutor, wait
    pool = ThreadPoolExecutor(max_workers=10)
    tasks = []
    future1 = pool.submit(run, 1)
    future2 = pool.submit(run, 2)
    tasks.append(future1)
    tasks.append(future2)
    print(future1.chanle())
    print(future1.done())
    print(future2.done())
    print(future1.result())
    print(future2.result())
    wait(future1)
    future3 = pool.submit(run, 2)
    print(future3.done())
    print(future3.result())
    print("===")


if __name__ == '__main__':
    test_deque()
