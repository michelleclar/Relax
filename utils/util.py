import cv2
import os
import glob
import time as t
import pyautogui
import numpy as np
from concurrent.futures import ThreadPoolExecutor, wait


# 生成随机字符串
def generate_random_string(length=8):
    import random
    import string
    characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choices(characters, k=length))
    return random_string


# opencv pyautogui
# 截图
def do_screenshot(screenshot_path, region):
    # 屏幕截图
    pyautogui.screenshot(screenshot_path, region)
    # 读取图片
    img = cv2.imread(screenshot_path)
    return img


# 模板匹配
# def do_match(target, template, is_debug):
#     result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
#     # min_loc 左上角
#     min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
#     height, width = template.shape[:2]
#     # 右下角
#     lower_right = (min_loc[0] + width, min_loc[1] + height)
#     avg = [
#         (int((min_loc[0] + lower_right[0]) / 2)),
#         (int((min_loc[1] + lower_right[1]) / 2))]
#     if is_debug:
#         # 绘制矩形边框，将匹配区域标注出来
#         # min_loc：矩形定点
#         # (min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
#         # (0,0,225)：矩形的边框颜色；2：矩形边框宽度
#         strmin_val = str(min_val)
#         cv2.rectangle(target, min_loc, (min_loc[0] + width, min_loc[1] + height), (0, 0, 225), 2)
#         # 显示结果,并将匹配值显示在标题栏上
#         cv2.imshow("MatchResult----MatchingValue=" + strmin_val, target)
#         cv2.waitKey()
#         cv2.destroyAllWindows()
#     return [(max_val - min_val), avg]


def do_match(target, template):
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    # min_loc 左上角
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return [(max_val - min_val), min_loc]


# 得到中点坐标
def get_cent_xy(avg, box):
    height, width = box
    lower_right = (avg[0] + width, avg[1] + height)
    return [
        (int((avg[0] + lower_right[0]) / 2)),
        (int((avg[1] + lower_right[1]) / 2))]


def get_random_xy(avg, box):
    import random
    height, width = box
    x, y = avg
    x += random.uniform(0, height)
    y += random.uniform(0, width)
    return [x, y]


# 模板匹配debug
def match_debug(target, result, box):
    """

    :param target: 需要标注的图片
    :param result: 匹配结果
    :param box: 模板图片
    :return:
    """
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    height, width = box[0], box[1]
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


# 左键单击事件（按下松开）
def left_click(avg):
    """
    :param var_avg:
    :return:
    """
    pyautogui.click(avg[0], avg[1], button='left')


# 获取当前屏幕分辨率
def current_resolution():
    return pyautogui.size()


# 预加载图像处理
def cv2_imread(path):
    return cv2.imread(path)


# 保存图片
def save_img(path, img):
    cv2.imencode('.png',img)[1].tofile(path)
    # cv2.imwrite(path, img)


# time
# 得到当前时间
def get_current_timestamp():
    return t.time()


# 时间元组
def get_current_struct_time():
    return t.localtime()


# 格式化当前时间
def format_time(format, time=None):
    if time is None:
        time = t.localtime()
    return t.strftime(format, time)


# thread
# 任务池化
def task_pool(*args):
    tasks = []
    for arg in args:
        task = ThreadPoolExecutor().submit(*arg)
        tasks.append(task)
        sleep(1)

    wait(tasks)


# 休眠
def sleep(time):
    t.sleep(max(0, time))


# numpy
# 数组初始化
def init_arr_obj(length, obj):
    return np.full(length, obj)


# 进行图像比较 返回是否匹配成功
def compare_img(img1, img2, sore=10):
    # Resize one of the images to match the dimensions of the other
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    # 结果越小越好
    mse = np.mean((img1 - img2) ** 2)
    return mse < sore


def clear(folder_path, type=None):
    if type is None:
        type = ['*.png', '*.jpg']
    files = glob.glob(os.path.join(folder_path, *type))
    for file in files:
        try:
            os.remove(file)
            print(f"Deleted: {file}")
        except Exception as e:
            print(f"Error deleting {file}: {str(e)}")


if __name__ == '__main__':
    start = t.localtime()
    before_click = f'{format_time("%H.%M.%S", start)}before-{112}'
    print(before_click)
    save_img(f"../imgs/fail/click/{before_click}.png", cv2_imread('../imgs/test_step1.png'))
    after_click = f'{format_time("%H.%M.%S")}after-{111}'
    print(after_click)
    save_img(f"../imgs/fail/click/{after_click}.png", cv2_imread('../imgs/test_step1.png'))
    # print(format_time("%H:%M:%S"))
    # save_img("../imgs/fail/click/12.43.08before112.png",cv2_imread('../imgs/test_step1.png'))
    # compare_img(cv2_imread('../imgs/test_step1.png'), cv2_imread('../imgs/test_step2.png'))
    # for i in range(100):
    #     print(get_random_xy([20,0],[10.01,100.01]))
    # clear(f"../imgs/screenshot")
    # print(t.strftime("%H:%M:%S", t.localtime()))
