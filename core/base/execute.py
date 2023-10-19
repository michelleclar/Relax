from build import Build, ClickStrategy, Strategy, MatchRule
from commons import img_name, exception
from utils import util, format
from core.base import image, screet, log

# 执行方法
logger = log.get_logger()


class Execute(object):
    """运行构建器构建的参数"""

    def execute(self, task: [Build.BuildTaskArgs]):
        """根据类型执行不同的执行方式"""
        task_type = type(task)
        match task_type:
            case Build.BuildTaskArgs:
                self.execute_task_args(task)
            case _:
                logger.error(f'不支持此类型：{task_type}')

    def execute_task_args(self, task: Build.BuildTaskArgs):
        """正式开始执行"""
        screenshot_name = "screenshot" + util.generate_random_string(4)
        # 进行区域处理
        region = screet.get_region_by_title(task.win_title)
        # 截图
        screet.do_screenshot(screenshot_name, region)
        head = task.get_head()
        imgs = set()
        graph = task.get_graph()
        
        times = util.init_arr_obj(len(task.nodes) + 1, -1)
        temp = util.get_current_timestamp()


        scrreenshot = image.cv2_imread(f"../imgs/screenshot/{screenshot_name}.png")

        node = head
        type = type(node.match_rule)
        match type:
            case MatchRule.Template:
                """模板匹配"""
                rule = node.match_rule
                template = image.cv2_imread(f"../imgs/{rule.template_name}.png")
                threshold, min_loc = image.do_match(scrreenshot, template)
                if threshold > rule.threshold:
                    # 匹配成功
                    height, width = template.shape[:2]
                    point = util.get_xy(node.strategy, min_loc, [height, width])
                    util.click(point, node.button.value)
                    util.sleep(1)
                else:
                    # 匹配失败
                    pass

            case MatchRule.Ocr:
                # Ocr
                pass
                """ocr"""


