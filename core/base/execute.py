from build import Build, ClickStrategy, Strategy, MatchRule
from commons import img_name, exception
from utils import util, format
from core.base import image, screet, log
# 执行方法
logger = log.get_logger()

class Execute(object):
    """运行构建器构建的参数"""
    def __init__(self):
        # 任务循环次数
        from commons.const import init,execute_consts
        init()
        self.retry_time = execute_consts['RetryTime']
        self.retry_count = execute_consts['RetryCount']
        self.task_loop = execute_consts['TaskLoop']
    def execute(self, task: [Build.BuildTaskArgs]):
        """根据类型执行不同的执行方式"""
        task_type = type(task)
        match task_type:
            case Build.BuildTaskArgs:
                self.execute_task_args(task)
            case _:
                logger.error(f'不支持此类型：{task_type}')
                
    def do_screenshot(self,region,screenshot_path: str):
        """截图操作,后续可能会处理成流""" 
        screet.do_screenshot(screenshot_path, region)
        return image.imread(screenshot_path)
    
    def init_screenshot(self,win_title: str):
        """截图预热"""
        screenshot_name = "screenshot" + util.generate_random_string(4)
        # 进行区域处理
        region = screet.get_region_by_title(win_title)
        screenshot_path = f"../imgs/screenshot/{screenshot_name}.png"        
        return region,screenshot_path
    
    def execute_task_args(self, task: Build.BuildTaskArgs):
        """正式开始执行"""
        head = task.get_head()
        times = util.init_arr_obj(len(task.nodes) + 1, -1)

        # TODO 将image和screet 进行整合
        region , screenshot_path = self.init_screenshot(task.win_title)
        
        temp = util.get_current_timestamp()
        
        start_time = util.get_current_timestamp()
        scrreenshot = self.do_screenshot(region=region,screenshot_path=screenshot_path)
        node = head
        try:
            util.do_execute(node,scrreenshot=scrreenshot)
        except expression as identifier:
            pass
        util.sleep(time[i+1]) 
        start = util.get_current_timestamp()
        
        times[i] = (
            times[i]
            if (times[i] != -1) and ((times[i] - start - temp) < 0)
            else start - temp
        )
        temp = start
