from utils import img_name, click


if __name__ == '__main__':
    while True:
        click.auto_click(img_name.active_start, "活动开始界面")
        click.auto_click(img_name.active_award,"资源结算界面",0,300)
        click.auto_click(img_name.active_vector,"战斗胜利界面")


