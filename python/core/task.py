from python.commons import img_name
from python.commons import exception
from python.commons.utils import util, format
from python.core.base import simulate
from python.core.base import cv, log

# 创建一个字典

logger = log.get_logger()


# 脚本任务类
# 任务参数设置  将点击延迟和随机点击迁移到点击事件名中
# 整体参数结构设计
# 匹配规则，ocr匹配:需要有匹配的文字参数 模板匹配:需要模板图片名字
# 点击事件名，点击事件
class ScriptTask:
    def __init__(self, args):
        self.args = args  # 运行流程的参数
        self.W, self.H = simulate.current_resolution()
        self.is_debug = False  # 是否开启debug
        self.template_threshold = 0.9  # 置信度 默认0.8
        self.region = (0, 0, self.W, self.H)
        self.screenshot_name = "screenshot" + util.generate_random_string(4)
        self.templates = {}
        self.img = None
        self.random = False  # false 表示区中点
        self.delay = 1
        for arg in args:
            img = cv.imread(f"../imgs/{arg[0]}.png")
            self.templates[arg[0]] = img

    def set_region(self, region):
        self.region = region
        return self

    def set_debug(self, is_debug):
        self.is_debug = is_debug
        return self

    def set_template_threshold(self, template_threshold):
        self.template_threshold = template_threshold
        return self

    def set_random(self, random):
        self.random = random
        return self

    def get_xy(self, template):
        """
        :param template:
        :return:匹配的xy
        """
        # 获取图片坐标
        res = self.do_match(template)
        # 使用模板匹配的置信度进行比较
        if res[0] > self.template_threshold:
            height, width = self.templates[template].shape[:2]
            if self.random:
                avg = util.get_random_xy(res[1], [height, width])
                r = self.get_real_xy(avg)
                logger.info(
                    f"最佳匹配模板坐标左上角:{res[1]},随机范围：{height, width},random===>{avg}"
                )
                return r
            else:
                avg = util.get_cent_xy(res[1], [height, width])
                r = self.get_real_xy(avg)
                logger.info(f"最佳匹配模板坐标左上角:{res[1]},box：{height, width},center===>{avg}")
                return r
        else:
            # 匹配失败，返回None
            return None

    def auto_click(self, img_model_path, name, coordinates=None):
        if coordinates is None:
            coordinates = [0, 0]
        start = util.get_current_struct_time()
        self.img = self.do_screenshot()
        avg = self.get_xy(img_model_path)

        if avg is None:
            raise exception.NOT_MATCH_EXCEPTION(f"😐😐😐没有匹配{name},retry")
        logger.info("🖱️🖱️🖱️正在点击：{}，坐标xy：{}，{}", name, avg[0], avg[1])
        x, y = coordinates
        x += avg[0]
        y += avg[1]
        x, y = self.real_check_xy([x, y])
        simulate.left_click([x, y])
        # 判断是否点击成功
        img = self.do_screenshot()
        if cv.compare_img(self.img, img, 3):
            # 可能没有进行点击
            before_click = f"{util.format_time(format.ONLY_TIME, start)}before-{name}"
            cv.save_img(f"../imgs/fail/click/{before_click}.png", self.img)
            after_click = f"{util.format_time(format.ONLY_TIME)}after-{name}"
            cv.save_img(f"../imgs/fail/click/{after_click}.png", img)
            raise exception.CLICK_EXCEPTION(f"👿👿👿疑似没有点击{name}，坐标xy：{x}，{y}")
        logger.info(f"✔️✔️✔️点击成功：{name}，坐标xy：{x}，{y}")
        return self

    def do_screenshot(self):
        path = f"../imgs/screenshot/{self.screenshot_name}.png"
        simulate.do_screenshot(path, self.region)
        return cv.cv2_imread(path)

    def do_match(self, template):
        return cv.do_match(self.img, self.templates[template])

    def get_real_xy(self, avg):
        return [avg[0] + self.region[0], avg[1] + self.region[1]]

    def real_check_xy(self, avg):
        return [
            min(self.region[2] + self.region[0], avg[0]),
            min(self.region[3] + self.region[1], avg[1]),
        ]

    def check_xy(self, avg):
        return [min(self.region[2], avg[0]), min(self.region[3], avg[1])]

    def sleep(self, time):
        util.sleep(time)

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

        times = util.init_arr_obj(len(self.args) + 1, -1)
        temp = util.get_current_timestamp()
        for j in range(count):
            for i, arg in enumerate(self.args):
                # 此次点击开始时间戳

                # 计算点击间隔 start -temp ： 为 间隔时间
                # TODO 优化 需要将上一次时间考虑进去
                # 将此次时间 进行记录到arg中
                # 记录上一次点击的开始时间

                start_time = util.get_current_timestamp()
                while util.get_current_timestamp() - start_time < max_duration:
                    try:
                        self.auto_click(*arg).sleep(times[i + 1])
                        # 检查点击是否有效
                    except exception.NOT_MATCH_EXCEPTION as e:
                        # Handle the custom exception (e.g., log it)
                        logger.warning(e)
                        util.sleep(1)
                        continue
                    except exception.CLICK_EXCEPTION as e:
                        logger.warning(f"{e},retry")
                        continue
                    except Exception as e:
                        logger.error(f"😭😭😭{log.detail_error()}")
                        raise e
                    else:
                        # Operation was successful, break out of the loop
                        break
                else:
                    # Max retries exceeded, raise an exception or handle it as needed
                    logger.warning(f"🙃🙃🙃{max_duration}秒点击失败：{arg}")

                start = util.get_current_timestamp()
                times[i] = (
                    times[i]
                    if (times[i] != -1) and ((times[i] - start - temp) < 0)
                    else start - temp
                )
                temp = start
            times[len(times) - 1] = times[0]
            logger.debug(f"时间优化间隔:{times}")
            max_duration = max(times) + 1


def main():
    region1 = (6, 36, 830, 463)
    region2 = (870, 36, 830, 454)
    """
    :arg 格式标准
    图片名必须 ， 点击事件名（必须，用于日志检查），偏移（可选），点击间隔（可选，不推荐代码会自动优化点击间隔）
    """
    # args = [(img_name.active_start, "活动开始界面"), (img_name.active_award, "资源结算界面", (0, 240)),
    #         (img_name.active_vector, "战斗胜利界面")]
    # args = [(img_name.test_1, "式神录"), (img_name.test_2, "返回")]
    args = [(img_name.ready, "准备")]
    # 使用 map() 函数将每个元素添加到容器中
    count = 900
    util.task_pool(
        (ScriptTask(args).set_region(region1).run, count),
        (ScriptTask(args).set_region(region2).run, count),
    )
    # util.task_pool((ScriptTask(args).set_region(region1).run, count))
    # util.task_pool((ScriptTask(args).set_region(region2).run, 800))


if __name__ == "__main__":
    main()
