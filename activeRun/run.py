from utils import img_name, click, get_vector

start = 0
end = 0
time = end - start

class ScriptTask:
    def __init__(self, region):
        self.region = region  # 初始化对象时传入 region 参数

    def run(self,args):
        click.auto_click(args,self.region)
        # 在这里定义你的方法
        print(f"Performing action in region {self.region}")

def run():
    args = [(img_name.active_start, "活动开始界面", time), (img_name.active_award, "资源结算界面", 0, 0, 400),
            (img_name.active_vector, "战斗胜利界面")]
    while True:
        for arg in args:
            click.auto_click(*arg)



if __name__ == '__main__':
    run()
    # while True:
    #     click.auto_click(img_name.active_start, "活动开始界面")
    #     click.auto_click(img_name.active_award, "资源结算界面", 0, 0, 400)
    #     click.auto_click(img_name.active_vector, "战斗胜利界面")
