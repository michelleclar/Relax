import cv2
import numpy as np
from core.base.structs import BOX

"""
图片操作
"""
# cache 
imgs = {}


def do_match(target, template):
    """
    模板匹配
    :param target: 目标图像
    :param template: 模板图像
    :return: 置信度 最佳匹配左上角
    """
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    # min_loc 左上角
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return [(max_val - min_val), min_loc]


def do_match(target, template, DEBUG=None):
    """
    模板匹配
    :param target: 目标图像
    :param template: 模板图像
    :return: 置信度 最佳匹配左上角
    """
    result = cv2.matchTemplate(target, template, cv2.TM_SQDIFF_NORMED)
    # min_loc 左上角
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    if DEBUG:
        match_debug(target=target, result=result, box=template.shape[:2])
    return [(max_val - min_val), min_loc]


def match_debug(target, result, box):
    """
    模板匹配debug
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


def rectangle(target, min_loc, box: BOX):
    cv2.rectangle(target, min_loc, (min_loc[0] + box.width, min_loc[1] + box.height), (0, 0, 225), 2)


def cache_imread(path):
    """
    读取图片
    :param path:
    :return:
    cv2.imread 返回值是 一个RGB NumPy
    三维数组，其中第一维表示像素的行数，第二维表示像素的列数，第三维表示像素的通道数
    """
    if path not in imgs.keys():
        imgs[path] = cv2.imread(path)
    return imgs[path]


def imread(path):
    """
    读取图片
    :param path:
    :return:
    cv2.imread 返回值是 一个RGB NumPy
    三维数组，其中第一维表示像素的行数，第二维表示像素的列数，第三维表示像素的通道数
    """
    return cv2.imread(path)


# 保存图片
def save_img(path, img):
    """
    保存图片
    :param path:
    :param img: NumPy 数组 3通道
    :return:
    cv2.imwrite 保存中文会乱码
    """
    cv2.imencode('.png', img)[1].tofile(path)
    # cv2.imwrite(path, img)


# 进行图像比较 返回是否匹配成功
def compare_img(img1, img2, sore=10):
    """
    图像相似比较
    :param img1:
    :param img2:
    :param sore:
    :return:
    """
    # Resize one of the images to match the dimensions of the other
    if img1.shape != img2.shape:
        img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))
    # 结果越小越好
    mse = np.mean((img1 - img2) ** 2)
    return mse < sore


# 创建一个回调函数，用于处理鼠标事件
def select_region(event, x, y, flags, param):
    global top_left_pt, bottom_right_pt, selecting

    # 当按下鼠标左键时，开始选择区域
    if event == cv2.EVENT_LBUTTONDOWN:
        top_left_pt = (x, y)
        selecting = True

    # 当释放鼠标左键时，结束选择区域
    elif event == cv2.EVENT_LBUTTONUP:
        bottom_right_pt = (x, y)
        selecting = False


def open_video(region):
    # 打开视频流
    cap = cv2.VideoCapture(0)

    # 创建一个窗口，并将回调函数绑定到窗口中
    cv2.namedWindow("Video Stream")
    cv2.setMouseCallback("Video Stream", select_region)

    # 循环从视频流中读取帧
    while True:
        ret, frame = cap.read()

        if not ret:
            break

        # 如果正在选择区域，绘制一个矩形框显示选择的区域
        if selecting:
            cv2.rectangle(frame, top_left_pt, bottom_right_pt, (0, 255, 0), 2)

        # 显示视频帧
        cv2.imshow("Video Stream", frame)

        # 按下 'q' 键退出循环
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # 根据选择的区域截取图像
    selected_region = frame[top_left_pt[1]:bottom_right_pt[1], top_left_pt[0]:bottom_right_pt[0]]

    # 保存截图
    cv2.imwrite("selected_region.png", selected_region)

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
