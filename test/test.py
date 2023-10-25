import threading
import time
from collections import deque
import asyncio
from core.base.execute import Build, ScriptArgs, MatchRule, Strategy, Policy
from core.base.structs import POINT
import cv2


def test_deque():
    a1 = ScriptArgs(task_name="开始", strategy=Strategy.ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("action"))
    a2 = ScriptArgs(task_name="失败", strategy=Strategy.ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("failed"))

    a3 = ScriptArgs(task_name="结算", strategy=Strategy.ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("settle"))
    a4 = ScriptArgs(task_name="结束", strategy=Strategy.ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("end"))
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


def test_autpjmp():
    a1 = ScriptArgs(task_name="开始", strategy=Strategy.ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("action"))
    a2 = ScriptArgs(task_name="失败", strategy=Strategy.ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("failed"))

    a3 = ScriptArgs(task_name="结算", strategy=Strategy.ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("settle"))
    a4 = ScriptArgs(task_name="结束", strategy=Strategy.ClickStrategy(Strategy.CENTER),
                    match_rule=MatchRule().template("end"))
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
        start_time = now()
        while now() - start_time < 10:

            # 批量处理
            for node in nodes:
                print(node)

                down = dag.downstream(node)
                if len(down) != 0:
                    q.append(down)
                continue
            break
        else:
            # Max retries exceeded, raise an exception or handle it as needed
            print(f"🙃🙃🙃{10}秒点击失败：{str(node)}")


def test_match():
    strategy = Strategy.ClickStrategy()

    match type(strategy):
        case Strategy.ClickStrategy:
            print(1)

        case Strategy.InputKeyStrategy:
            print(2)


def test_dag():
    a1 = ScriptArgs(task_name="开始", strategy=Strategy.ClickStrategy(Policy.CENTER),
                    match_rule=MatchRule().template("action"))
    a2 = ScriptArgs(task_name="失败", strategy=Strategy.ClickStrategy(Policy.CENTER),
                    match_rule=MatchRule().template("failed"))

    a3 = ScriptArgs(task_name="结算", strategy=Strategy.ClickStrategy(Policy.CENTER),
                    match_rule=MatchRule().template("settle"))
    a4 = ScriptArgs(task_name="结束", strategy=Strategy.ClickStrategy(Policy.CENTER),
                    match_rule=MatchRule().template("end"))
    task = Build().BuildTaskArgs(win_title="aaa", task_loop=10)
    task.add_nodes({a1, a2, a3, a4})
    task.add_edge(a1, a2)
    task.add_edge(a1, a3)
    task.add_edge(a3, a4)
    task.build()
    dag = task.dag
    r1 = dag.ind_nodes()
    r2 = dag.all_leaves()
    r3 = dag.all_downstreams(a1)
    print([str(x) for x in task.nodes])
    print("======")


def test_struct():
    p = POINT(x=1, y=1)
    p.x += 1
    p.y += 1
    print(p)


q = deque()


def push(i):
    t = threading.current_thread()
    for j in range(i):
        push_element(f"{j} + {t.name}")


def push_element(element: any):
    time.sleep(1)
    q.append(element)



def test_queue():
    tasks = []
    for i in range(10):
        task = threading.Thread(target=push, args=(tuple([10])))
        tasks.append(task)
    for task in tasks:
        task.start()
    start = now()
    count = 0
    while now() - start < 20:

        while len(q) != 0:
            e = q.pop()
            count += 1
            print(e)
    print(count)


if __name__ == '__main__':
    test_queue()
