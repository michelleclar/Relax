import cv2
import pyautogui


def get_xy(img_model_path, ocr=False, template_threshold=0.8):
    """
    :param img_model_path:模型图片名称
    :return:匹配的xy
    """
    # 屏幕截图
    pyautogui.screenshot().save("../imgs/screenshot/screenshot.png")
    # 保存图片到指定路径
    img = cv2.imread("../imgs/screenshot/screenshot.png")
    # 模板匹配
    img_template = cv2.imread(f'../imgs/{img_model_path}.png')
    # 获取图片坐标
    result = cv2.matchTemplate(img, img_template, cv2.TM_SQDIFF_NORMED)
    if ocr:
        # 保存路径
        path = f'../imgs/result_imgs/{img_model_path}.png'

        upper_left = cv2.minMaxLoc(result)[2]
        # 在img上标记匹配位置
        cv2.rectangle(img, upper_left, (upper_left[0] + img_template.shape[1], upper_left[1] + img_template.shape[0]),
                      (0, 0, 255), 2)
        roi = img[upper_left[1]:upper_left[1] + img_template.shape[0],
              upper_left[0]:upper_left[0] + img_template.shape[1]]
        cv2.imwrite(path, roi)

    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    # 使用模板匹配的置信度进行比较
    if (max_val - min_val) > template_threshold:
        # 匹配成功，返回坐标（这里假设坐标为左上角）
        height, width, channels = img_template.shape
        lower_right = (min_loc[0] + width, min_loc[1] + height)

        avg = (int((min_loc[0] + lower_right[0]) / 2), int((min_loc[1] + lower_right[1]) / 2))
        # x, y = min_loc
        return avg
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


if __name__ == '__main__':
    res = get_xy("active_start")
    # box = get_box("start_game",True)
    # print(box)
