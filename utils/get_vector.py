import cv2
import pyautogui
import numpy as np

H = 1440
W = 2560


def get_xy(img_model_path, region=None, is_dbug=False, template_threshold=0.8):
    """
    :param template_threshold:
    :param is_dbug:
    :param region:
    :param img_model_path:模型图片名称
    :return:匹配的xy
    """
    # 屏幕截图
    pyautogui.screenshot("../imgs/screenshot/screenshot.png", region)
    # .save("../imgs/screenshot/screenshot.png"))
    # 保存图片到指定路径
    img = cv2.imread("../imgs/screenshot/screenshot.png")
    # 模板匹配
    img_template = cv2.imread(f'../imgs/{img_model_path}.png')
    # 获取图片坐标
    if region is not None:
        res = do_match(img, img_template, region, is_dbug)
    else:
        res = do_match(img, img_template, is_dbug)
    # 使用模板匹配的置信度进行比较
    if res[0] > template_threshold:
        return res[1]
    else:
        # 匹配失败，返回None
        return None


def get_box(img_model_path, ocr=False):
    """
    :param img_model_path:模型图片名称
    :return:匹配的xy坐标区域
    """
    # 屏幕截图
    pyautogui.screenshot().save("../imgs/screenshot/screenshot.png")
    # 保存图片到指定路径
    img = cv2.imread("../imgs/screenshot/screenshot.png")
    # 模板匹配
    img_template = cv2.imread(f'../imgs/{img_model_path}.png')
    # 获取图片坐标
    height, width, channels = img_template.shape

    # 获取匹配区域坐标
    result = cv2.matchTemplate(img, img_template, cv2.TM_SQDIFF_NORMED)
    upper_left = cv2.minMaxLoc(result)[2]
    lower_right = (upper_left[0] + width, upper_left[1] + height)

    if ocr:
        # 保存路径
        path = f'../imgs/result_imgs/{img_model_path}.png'

        # 在img上标记匹配位置
        cv2.rectangle(img, upper_left, lower_right, (0, 0, 255), 2)
        roi = img[upper_left[1]:lower_right[1], upper_left[0]:lower_right[0]]
        cv2.imwrite(path, roi)

    # 返回匹配区域坐标
    return [upper_left[0], upper_left[1], lower_right[0], lower_right[1]]


def single_match(img_model_path, ocr=False, template_threshold=0.8):
    # 屏幕截图
    pyautogui.screenshot().save("../imgs/screenshot/screenshot.png")
    # 保存图片到指定路径
    target = cv2.imread("../imgs/screenshot/screenshot.png")
    # 模板匹配
    template = cv2.imread(f'../imgs/{img_model_path}.png')
    # 获取图片坐标
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    # 获得模板图片的高宽尺寸
    theight, twidth = template.shape[:2]
    # 归一化处理
    cv2.normalize(result, result, 0, 1, cv2.NORM_MINMAX, -1)
    # 寻找矩阵（一维数组当做向量，用Mat定义）中的最大值和最小值的匹配结果及其位置
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    # 匹配值转换为字符串
    # 对于cv2.TM_SQDIFF及cv2.TM_SQDIFF_NORMED方法min_val越趋近与0匹配度越好，匹配位置取min_loc
    # 对于其他方法max_val越趋近于1匹配度越好，匹配位置取max_loc
    strmin_val = str(min_val)
    # 绘制矩形边框，将匹配区域标注出来
    # min_loc：矩形定点
    # (min_loc[0]+twidth,min_loc[1]+theight)：矩形的宽高
    # (0,0,225)：矩形的边框颜色；2：矩形边框宽度
    cv2.rectangle(target, min_loc, (min_loc[0] + twidth, min_loc[1] + theight), (0, 0, 225), 2)
    # 显示结果,并将匹配值显示在标题栏上
    cv2.imshow("MatchResult----MatchingValue=" + strmin_val, target)
    cv2.waitKey()
    cv2.destroyAllWindows()


def single_more_match(img_model_path, ocr=False, template_threshold=0.8):
    # 屏幕截图
    # 使用 pyautogui 库截取屏幕，并保存到指定路径

    pyautogui.screenshot().save("../imgs/screenshot/screenshot.png")

    # 保存图片到指定路径
    # 将截图后的图片保存到指定路径

    target = cv2.imread("../imgs/screenshot/screenshot.png")

    # 将原始图像转换为灰度图像
    # 使用 cv2.cvtColor() 函数将原始图像转换为灰度图像，以便进行模板匹配

    img_gray = cv2.cvtColor(target, cv2.COLOR_BGR2GRAY)

    # 模板匹配
    # 使用 cv2.matchTemplate() 函数进行模板匹配，获取匹配结果

    template = cv2.imread(f'../imgs/{img_model_path}.png', 0)
    h, w = template.shape[:2]

    res = cv2.matchTemplate(img_gray, template, cv2.TM_CCOEFF_NORMED)

    # 获取匹配程度大于指定阈值的坐标
    # 使用 np.where() 函数获取匹配程度大于指定阈值的坐标

    threshold = 0.8
    loc = np.where(res >= threshold)

    # np.where返回的坐标值(x,y)是(h,w)，注意h,w的顺序
    # 将 np.where() 函数返回的坐标值逆序，以便正确绘制矩形框

    for pt in zip(*loc[::-1]):
        # 计算矩形框的右下角坐标
        bottom_right = (pt[0] + w, pt[1] + h)

        # 在原始图像上画出矩形框
        cv2.rectangle(target, pt, bottom_right, (0, 0, 255), 2)

    # 保存结果
    # 将处理后的图像保存到指定路径

    cv2.imwrite("img.jpg", target)

    # 显示结果
    # 使用 cv2.imshow() 函数显示处理后的图像

    cv2.imshow('img', target)

    # 等待用户输入
    # 使用 cv2.waitKey() 函数等待用户输入

    cv2.waitKey(0)

    cv2.destroyAllWindows()


def find_xy(img_model_path, ocr=False, template_threshold=0.8):
    """
     :param img_model_path:模型图片名称
     :return:匹配的xy
     :TODO 匹配完模板进行是否点击校验
     """
    # 屏幕截图
    pyautogui.screenshot().save("../imgs/screenshot/screenshot.png")
    # 保存图片到指定路径
    img = cv2.imread("../imgs/screenshot/screenshot.png")
    # 模板匹配
    img_template = cv2.imread(f'../imgs/{img_model_path}.png')

    res = do_match(img, img_template)

    if res[0] > template_threshold:
        return res[1]
    else:
        None


# 进行匹配
# 并返回 置信度 和 坐标
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


def do_match(target, template, region, is_debug=False):
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    height, width, channels = template.shape
    lower_right = (min_loc[0] + width, min_loc[1] + height)
    avg = (
        (int((min_loc[0] + lower_right[0]) / 2) + region[0]),
        (int((min_loc[1] + lower_right[1]) / 2)) + (H - height - region[1]))
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


class ScriptTask:
    args = []
    region = (0, 0, 2560, 1440)

    def __init__(self, region):
        self.region = region  # 初始化对象时传入 region 参数
        self.W, self.H = pyautogui.size()  # 获取当前屏幕分辨率

    def push_arg(self, *args):
        for arg in args:
            self.args.append(arg)

    def run(self, args):
        # 在这里定义你的方法
        print(f"Performing action in region {self.region}")


if __name__ == '__main__':
    region1 = (0, 0, 1280, 750)
    region2 = (1280, 0, 1280, 750)
    task1 = ScriptTask(region1)
    task2 = ScriptTask(region2)
    # res = get_xy("active_start",region1,True)
    # box = get_box("start_game",True)
    # print(box)
