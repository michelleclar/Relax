from utils import click
from commons import img_name
import cv2
import pyautogui
import time as t
start = 0
end = 0
time = end - start
def get_xy(img_model_path, is_dbug=False, template_threshold=0.8):
    """
    :param template_threshold:
    :param is_dbug:
    :param region:
    :param img_model_path:模型图片名称
    :return:匹配的xy
    """
    # 屏幕截图
    pyautogui.screenshot().save("../imgs/screenshot/screenshot.png")
    # .save("../imgs/screenshot/screenshot.png"))
    # 保存图片到指定路径
    img = cv2.imread("../imgs/screenshot/screenshot.png")
    # 模板匹配
    img_template = cv2.imread(f'../imgs/{img_model_path}.png')
    # 获取图片坐标

    res = do_match(img, img_template, is_dbug)
    # 使用模板匹配的置信度进行比较
    if res[0] > template_threshold:
        return res[1]
    else:
        # 匹配失败，返回None
        return None
def do_match(target, template, is_debug=False):
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    height, width, channels = template.shape
    lower_right = (min_loc[0] + width, min_loc[1] + height)

    avg = (int((min_loc[0] + lower_right[0]) / 2), int((min_loc[1] + lower_right[1]) / 2))
    if is_debug:
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

def click(var_avg, time=0):
    """
    :param var_avg:
    :return:
    """
    pyautogui.click(var_avg[0], var_avg[1], button='left')
    t.sleep(time)
def auto_click(img_model_path, name, time=0, x=0, y=0):
    avg = get_xy(img_model_path)
    if avg == None:
        print(f'没有匹配{name}')
        return False
    print(f'正在点击{name},坐标xy:{avg[0], avg[1]}')
    x += avg[0]
    y += avg[1]


    click((x, y), time)
    return True

def run():
    args = [(img_name.active_start, "活动开始界面", time), (img_name.active_award, "资源结算界面", 0, 0, 400),
            (img_name.active_vector, "战斗胜利界面")]
    while True:
        for arg in args:
            auto_click(*arg)



if __name__ == '__main__':
    run()
    # while True:
    #     click.auto_click(img_name.active_start, "活动开始界面")
    #     click.auto_click(img_name.active_award, "资源结算界面", 0, 0, 400)
    #     click.auto_click(img_name.active_vector, "战斗胜利界面")
