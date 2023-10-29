import numpy
from PIL.Image import Image

from core.base import cv, log
from paddleocr import PaddleOCR, draw_ocr
import cv2
import mss

logger = log.get_logger()


def get_text_center(img_name, text, avg_img_name, is_deg_recog=False):
    '''
    获取OCR识别文本的实际中心坐标

    :param img_name: 图像文件名
    :param text: 目标文本
    :param avg_img_name: 识别图片真实位置
    :param is_deg_recog: 是否进行倾斜矫正
    :return: 文本实际中心坐标，如果未找到匹配的文本则返回None
    '''
    path = f'../imgs/result_imgs/{img_name}.png'
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    # 图片中心x,y
    avg_pic = get_image_center(path)
    x_scale = avg_pic[0] / avg_img_name[0]
    y_scale = avg_pic[1] / avg_img_name[1]
    result = ocr.ocr(path, cls=True)

    for idx in range(len(result[0])):
        if idx == 1:
            return (avg_pic / x_scale, avg_pic[1] / y_scale)
        res = result[0][idx]
        for i in range(len(res[0])):
            s = res[1][0]
            if s == text:
                # 计算左上角和右下角点的坐标
                x1, y1 = res[0][0]
                x2, y2 = res[0][1]
                x3, y3 = res[0][2]
                x4, y4 = res[0][3]
                x_min = min(x1, x2, x3, x4)
                x_max = max(x1, x2, x3, x4)
                y_min = min(y1, y2, y3, y4)
                y_max = max(y1, y2, y3, y4)
                # 计算中心点坐标
                avg = ((x_min + x_max) / 2, (y_min + y_max) / 2)
                avg = (avg[0] / x_scale, avg[1] / y_scale)
                if is_deg_recog:
                    deg_ocr(img_name, result[0], path)
                return avg
    logger.warning('未找到匹配的文本,识别的信息: %s', result[0])
    return None


def do_ocr(img_name, deg=False):
    path = f'../imgs/result_imgs/{img_name}.png'
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    result = ocr.ocr(path, cls=True)
    text = result[0][0][1][0]
    confidence = result[0][0][1][1]
    if deg:
        deg_ocr(img_name, result[0], path)
    return confidence > 0.7 and text or None


def deg_ocr(img_name, result, path):
    # image = Image.open(path).convert('RGB')
    img = cv.imread(path)
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(img, boxes, txts, scores, font_path='./fonts/simfang.ttf')
    im_show = cv2.imdecode(im_show.astype("uint8"), cv2.IMREAD_COLOR)
    # im_show = Image.fromarray(im_show)im_show = cv2.imdecode(im_show.astype("uint8"), cv2.IMREAD_COLOR)
    im_show.save(f'../imgs/ocr_result/{img_name}.png')


def ocrByPDF():
    # Paddleocr目前支持的多语言语种可以通过修改lang参数进行切换
    # 例如`ch`, `en`, `fr`, `german`, `korean`, `japan`
    ocr = PaddleOCR(use_angle_cls=True, lang="ch",
                    page_num=2)  # need to run only once to download and load model into memory
    img_path = './xxx.pdf'
    result = ocr.ocr(img_path, cls=True)
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            print(line)

    # 显示结果
    import fitz
    from PIL import Image
    import cv2
    import numpy as np
    imgs = []
    with fitz.open(img_path) as pdf:
        for pg in range(0, pdf.pageCount):
            page = pdf[pg]
            mat = fitz.Matrix(2, 2)
            pm = page.getPixmap(matrix=mat, alpha=False)
            # if width or height > 2000 pixels, don't enlarge the image
            if pm.width > 2000 or pm.height > 2000:
                pm = page.getPixmap(matrix=fitz.Matrix(1, 1), alpha=False)

            img = Image.frombytes("RGB", [pm.width, pm.height], pm.samples)
            img = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
            imgs.append(img)
    for idx in range(len(result)):
        res = result[idx]
        image = imgs[idx]
        boxes = [line[0] for line in res]
        txts = [line[1][0] for line in res]
        scores = [line[1][1] for line in res]
        im_show = draw_ocr(image, boxes, txts, scores, font_path='doc/fonts/simfang.ttf')
        im_show = Image.fromarray(im_show)
        im_show.save('result_page_{}.jpg'.format(idx))


def get_image_center(image_path):
    image_width, image_height = cv.imread(image_path)[:2]
    center_x = image_width // 2
    center_y = image_height // 2
    return center_x, center_y


def test_ocr():
    ocr = PaddleOCR(use_angle_cls=True, lang="ch")
    monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
    sct = mss.mss()
    sct_img = sct.grab(monitor)
    img = numpy.array(sct_img)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    from PIL import Image

    result = ocr.ocr(img, cls=True)
    for idx in range(len(result)):
        res = result[idx]
        for line in res:
            print(line)


    res = Image.frombytes('RGB', sct_img.size, sct_img.bgra, 'raw', 'BGRX')
    result = result[0]
    boxes = [line[0] for line in result]
    txts = [line[1][0] for line in result]
    scores = [line[1][1] for line in result]
    im_show = draw_ocr(res, boxes, txts, scores, font_path='./fonts/simfang.ttf')
    im_show = Image.fromarray(im_show)
    im_show.save('result.jpg')


if __name__ == '__main__':
    # get_xy("jjtp",True)
    # screet.do_screenshot("../imgs/screenshot/screenshot.png")
    test_ocr()
    # num = text.split('/')[0]
    # print(num)
    # avg = get_xy("start_game", True)
    # print(avg)
    # text = get_text_center("start_game", "进入游戏", avg, True)
    # print(text)
