from utils import get_vector, do_ocr, click



def auto_click(img_model_path, name):
    avg = get_xy(img_model_path, False)
    print(f'正在点击{name},坐标xy:{avg[0], avg[1]}')
    click(avg)


# get_xy("jiejie_num",True)
# auto_click("start_game","进入游戏")
