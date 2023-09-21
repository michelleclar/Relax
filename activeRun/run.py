from utils import img_name, click, get_vector
import goto
from dominate.tags import label
from goto import with_goto


@with_goto
def run():
    label.start
    if click.auto_click(img_name.active_start, "活动开始界面"):
        goto.start
    else:
        goto.award

    label.award
    if click.auto_click(img_name.active_award, "资源结算界面",0, 0, 300):
        goto.award
    else:
        goto.end

    label.end
    if click.auto_click(img_name.active_vector, "战斗胜利界面"):
        goto.end
    else:
        goto.start


if __name__ == '__main__':
    while True:
        click.auto_click(img_name.active_start, "活动开始界面")
        click.auto_click(img_name.active_award, "资源结算界面",0, 0, 300)
        click.auto_click(img_name.active_vector, "战斗胜利界面")
