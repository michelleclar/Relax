import logging
import time
from utils import get_vector, ocr, click, send
from utils.img_name import *

NUM = 15
count = 0

def run():
    if check_num():
        start()


# 执行结界突破逻辑
def check_num():
    # 保存匹配的实际图片 需要ocr,传入True
    get_vector.get_xy(jjtp_step1, True)
    text = ocr.do_ocr(jjtp_step1, True)
    try:
        count = int(text.split('/')[0])
    except ValueError:
        logging.ERROR("%s图片识别错误", jjtp_step1)
    return int(count) > NUM and True or False


def start():
    click.auto_click(jjtp_step2, "进入结界突破页面")
    # 判断是否进入结界突破界面
    get_vector.get_xy(jjtp_step3, True)
    text = ocr.do_ocr(jjtp_step3)
    if text != '刷新':
        # 没有进入
        start()
    # 先失败4次
    for i in range(4):
        click.auto_click(jjtp_step4, "清理结界")
        click.auto_click(jjtp_step5, '进攻')
        send.keys(['esc','enter'],2)
        click.click_current()
    for i in range(count):
        click.auto_click(jjtp_step4, "清理结界")
        click.auto_click(jjtp_step5, '进攻')
        click.click_current()
        time.sleep(5)



if __name__ == '__main__':
    # get_vector.get_xy(jjtp_step4,True)
    # click.auto_click(jjtp_step4,"清理结界")
    # click.auto_click(jjtp_step5,'进攻')
    # box = get_vector.get_box(jjtp_step4, True)
    # print(box[0], box[1], box[2], box[3])
    # cent_x = (box[0] + box[2]) / 2
    # cent_y = (box[1] + box[3]) / 2
    #
    # x_scale = (box[2] - box[0]) / 3
    # y_scale = (box[3] - box[1]) / 3
    # xy_1 = cent_x - x_scale,cent_y - y_scale
    # xy_2 = cent_y - y_scale
    # xy_3 = cent_x + x_scale,cent_y - y_scale
    # xy_4 = cent_x - x_scale
    # xy_6 = cent_x + x_scale
    # xy_7 = cent_x - x_scale,cent_y + y_scale
    # xy_8 = cent_y + y_scale
    # xy_9 = cent_x + x_scale,cent_y + y_scale
    run()
