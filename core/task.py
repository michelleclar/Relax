import pyautogui
import loguru

import numpy as np
import time as t

import cv2

from commons import img_name, exception

logger = loguru.logger


class ScriptTask:
    def __init__(self):
        self.args = []  # 运行流程的参数
        self.W, self.H = pyautogui.size()  # 获取当前屏幕分辨率
        self.is_debug = False  # 是否开启debug
        self.template_threshold = 0.8  # 置信度 默认0.8
        self.region = (0, 0, self.W, self.H)

    def set_region(self, region):
        self.region = region
        return self

    def set_debug(self, is_debug):
        self.is_debug = is_debug
        return self

    def set_template_threshold(self, template_threshold):
        self.template_threshold = template_threshold
        return self

    def get_xy(self, img_model_path):
        """
        :param img_model_path:模型图片名称
        :return:匹配的xy
        """
        # 屏幕截图
        pyautogui.screenshot("../imgs/screenshot/screenshot.png", self.region)
        # .save("../imgs/screenshot/screenshot.png"))
        # 保存图片到指定路径
        img = cv2.imread("../imgs/screenshot/screenshot.png")
        # 模板匹配
        img_template = cv2.imread(f'../imgs/{img_model_path}.png')
        # 获取图片坐标
        res = self.do_match(img, img_template)
        # 使用模板匹配的置信度进行比较
        if res[0] > self.template_threshold:
            return res[1]
        else:
            # 匹配失败，返回None
            return None

    def do_match(self, target, template):
        result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
        # min_loc 左上角
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        height, width, channels = template.shape
        # 右下角
        lower_right = (min_loc[0] + width, min_loc[1] + height)
        avg = (
            (int((min_loc[0] + lower_right[0]) / 2) + self.region[0]),
            (int((min_loc[1] + lower_right[1]) / 2)) + self.region[1])
        if self.is_debug:
            # 绘制矩形边框，将匹配区域标注出来
            # min_loc：矩形定点
            # (min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
            # (0,0,225)：矩形的边框颜色；2：矩形边框宽度
            strmin_val = str(min_val)
            cv2.rectangle(target, min_loc, (min_loc[0] + width, min_loc[1] + height), (0, 0, 225), 2)
            # 显示结果,并将匹配值显示在标题栏上
            cv2.imshow("MatchResult----MatchingValue=" + strmin_val, target)
            cv2.waitKey()
            cv2.destroyAllWindows()
        return ((max_val - min_val), avg)

    class Execute:
        x, y = 0, 0

        def __init__(self, x, y):
            self.x = x
            self.y = y

        def execute(self, time=0):
            self.click(time)

        def click(self, time=0):
            """
            :param var_avg:
            :return:
            """
            pyautogui.click(self.x, self.y, button='left')
            t.sleep(time)

    def click(self, var_avg, time=0):
        """
        :param var_avg:
        :return:
        """
        pyautogui.click(var_avg[0], var_avg[1], button='left')
        t.sleep(time)

    def auto_click(self, img_model_path, name, coordinates=None):
        if coordinates is None:
            coordinates = [0, 0]
        avg = self.get_xy(img_model_path)
        if avg is None:
            logger.warning("没有匹配{},retry", name)
            raise exception.NOT_FIND_Exception(f"没有匹配{name},retry")

        logger.info("正在点击：{}，坐标xy：{}，{}", name, avg[0], avg[1])
        x, y = coordinates
        x += avg[0]
        y += avg[1]

        return self.Execute(x, y)

    def execute(self, time):
        pass

    def push_arg(self, *args):
        for arg in args:
            self.args.append(arg)

    def run(self, count=100, max_duration=30):
        """

        :param max_duration:
        :param count: 流程运行次数 默认100次
        :return:
        """
        # 计算每次点击间隔 ，并将间隔 参数传递进去 计算时需要将上一次计算间隔忽略
        # 因为上一次间隔如果传入了时间参数会对后一次计算产生影响

        times = np.zeros(len(self.args) + 1)
        times[1] = 0
        temp = t.time()
        for j in range(count):
            for i, arg in enumerate(self.args):
                # 此次点击开始时间戳
                start = t.time()
                # 计算点击间隔 start -temp ： 为 间隔时间
                # TODO 优化 需要将上一次时间考虑进去
                times[i] = start - temp
                print(times[i],arg)
                # 将此次时间 进行记录到arg中
                # 记录上一次点击的开始时间
                temp = start
                start_time = t.time()
                while t.time() - start_time < max_duration:
                    try:
                        print(times[i+1])
                        self.auto_click(*arg).execute(times[i + 1])
                    except exception.NOT_FIND_Exception as e:
                        # Handle the custom exception (e.g., log it)
                        logger.warning(f"Custom exception caught: {e}")
                        t.sleep(1)
                        continue
                    else:
                        # Operation was successful, break out of the loop
                        break
                else:
                    # Max retries exceeded, raise an exception or handle it as needed
                    logger.error("{}秒点击失败：{}",max_duration,arg)
            logger.info("时间优化间隔:{}",times)

if __name__ == '__main__':
    region1 = (0, 0, 1280, 750)
    region2 = (1280, 0, 1280, 750)
    """
    :arg 格式标准 
    图片名必须 ， 点击事件名（必须，用于日志检查），偏移（可选），点击间隔（可选，不推荐代码会自动优化点击间隔）
    """
    args = [(img_name.active_start, "活动开始界面"), (img_name.active_award, "资源结算界面", (0, 400)),
            (img_name.active_vector, "战斗胜利界面")]
    task1 = ScriptTask().set_region(region1)
    task1.push_arg(*args)
    task1.run()
