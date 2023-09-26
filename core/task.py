from commons import img_name, exception
from utils import util, log, format

# 创建一个字典

logger = log.get_logger()

# 脚本任务类
"""
此包设计为不允许导入任何第三方依赖 目的是解耦
TODO 设计理念为通用脚本任务
只需要传递一些简单参数就可以运行
任务运行流程采用的数据结构为有向无环图

采用此数据结构的想法
借鉴工作流思想
args 为队列任务 即一个个点击事件 
每次点击事件失败 或者找不到对应元素都有对应处理 
点击事件失败
采用RGB像素比较 目前 对于模板进行缩小范围的算法优化有待测试 不知道有没有意义

找不到元素
此错误在加入了点击事件失败检查之后基本就不会出现
目前做法并没有遍历点击队列来处理 找不到元素的异常，
目前考虑是如果去遍历有可能 会执行上一次点击任务任 导致循序错乱 如果后面点击事件h都是正常的 这个遍历将会是不可避免的

脚本防封机制
目前做法是在匹配的区域进行随机random坐标

TODO 关于有些方法功能设计
在运行参数上 
    :arg 格式标准
    图片名必须 ， 点击事件名（必须，用于日志检查），偏移（可选)
    偏移我认为是必须要保留的参数位 
    但在脚本测试的过程中 发现有的模板匹配并不是点击对应匹配的位置 需要点击模板外的位置 那需要加一个参数来处理这个吗 还是只用偏移呢
    关于点击位置是做了检查的 第一次检查 是不允许点击匹配模板外的位置 第二次检查 不允许点击截图范围外的位置 
    所以理论上只要你偏移大小大于模板宽或者高 是可以做到百分百点击模板以外的位置 
    所以不打算进行 添加额外参数
目前待增加功能
当脚本正常运行 突然跳出一个蒙版 需要在什么时候去做
打算在 一次任务流运行完 进行处理 都不匹配 代表有突发事件

这个蒙版除了游戏内的可以进行处理 游戏外的应该如何操作
因为采用多线程进行脚本运行 暂时不打算处理游戏外的因素
"""
class ScriptTask:
    def __init__(self, args):
        self.args = args  # 运行流程的参数
        self.W, self.H = util.current_resolution()
        self.is_debug = False  # 是否开启debug
        self.template_threshold = 0.8  # 置信度 默认0.8
        self.region = (0, 0, self.W, self.H)
        self.screenshot_name = "screenshot" + util.generate_random_string(4)
        self.templates = {}
        self.img = None
        self.random = True  # false 表示区中点
        for arg in args:
            img = util.cv2_imread(f'../imgs/{arg[0]}.png')
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

    def set_random(self,random):
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
                logger.info(f'最佳匹配模板坐标左上角:{res[1]},随机范围：{height, width},random===>{avg}')
                return r
            else:
                avg = util.get_cent_xy(res[1], [height, width])
                r = self.get_real_xy(avg)
                logger.info(f'最佳匹配模板坐标左上角:{res[1]},box：{height, width},center===>{avg}')
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
            raise exception.NOT_FIND_Exception(f"😐😐😐没有匹配{name},retry")
        logger.info("🖱️🖱️🖱️正在点击：{}，坐标xy：{}，{}", name, avg[0], avg[1])
        x, y = coordinates
        x += avg[0]
        y += avg[1]
        x, y = self.real_check_xy([x, y])
        util.left_click([x, y])
        #判断是否点击成功
        img = self.do_screenshot()
        if util.compare_img(self.img, img,2):
            # 可能没有进行点击
            before_click = f'{util.format_time(format.ONLY_TIME, start)}before-{name}'
            util.save_img(f"../imgs/fail/click/{before_click}.png", self.img)
            after_click = f'{util.format_time(format.ONLY_TIME)}after-{name}'
            util.save_img(f"../imgs/fail/click/{after_click}.png", img)
            raise exception.NOT_FIND_Exception(f"👿👿👿疑似没有点击{name}，坐标xy：{x}，{y}")
        logger.info(f"✔️✔️✔️点击成功：{name}，坐标xy：{x}，{y}")
        return self

    def do_screenshot(self):
        return util.do_screenshot(f"../imgs/screenshot/{self.screenshot_name}.png", self.region)

    def do_match(self, template):
        return util.do_match(self.img, self.templates[template])

    def get_real_xy(self, avg):
        return [avg[0] + self.region[0], avg[1] + self.region[1]]

    def real_check_xy(self, avg):
        return [min(self.region[2] + self.region[0], avg[0]), min(self.region[3] + self.region[1], avg[1])]

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
                    except exception.NOT_FIND_Exception as e:
                        # Handle the custom exception (e.g., log it)
                        logger.warning(e)
                        util.sleep(1)
                        continue
                    except exception.NOT_CLICK_Exception as e:
                        logger.warning(f'{e},retry')
                        continue
                    except Exception as e:
                        logger.error(f'😭😭😭{log.detail_error()}')
                        raise e
                    else:
                        # Operation was successful, break out of the loop
                        break
                else:
                    # Max retries exceeded, raise an exception or handle it as needed
                    logger.warning(f"🙃🙃🙃{max_duration}秒点击失败：{arg}")

                start = util.get_current_timestamp()
                times[i] = times[i] if (times[i] != -1) and ((times[i] - start - temp) < 0) else start - temp
                temp = start
            times[len(times) - 1] = times[0]
            logger.debug(f"时间优化间隔:{times}")
            max_duration = max(times) + 1


if __name__ == '__main__':
    region1 = (0, 0, 1270, 740)
    region2 = (1290, 0, 1270, 740)
    """
    :arg 格式标准
    图片名必须 ， 点击事件名（必须，用于日志检查），偏移（可选），点击间隔（可选，不推荐代码会自动优化点击间隔）
    """
    args = [(img_name.active_start, "活动开始界面"), (img_name.active_award, "资源结算界面", (0, 400)),
            (img_name.active_vector, "战斗胜利界面")]
    # args = [(img_name.test_1, "式神录"), (img_name.test_2, "返回")]
    # 使用 map() 函数将每个元素添加到容器中

    util.task_pool((ScriptTask(args).set_region(region1).run, 800), (ScriptTask(args).set_region(region2).run, 800))
    # util.task_pool((ScriptTask(args).set_region(region2).run, 800))
    # util.task_pool((ScriptTask(args).set_region(region2).run, 800))
