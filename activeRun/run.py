from utils import img_name, click , get_vector
import goto
from dominate.tags import label
from goto import with_goto
@with_goto
def run():
    label .start
    if click.auto_click(img_name.active_start, "活动开始界面"):
        label .findstart
        res = get_vector.find_xy(img_name.active_start)
        if res != None:
            click.click(res)
            goto .findstart
        else: goto.award
    else: goto.award

    label .award
    if click.auto_click(img_name.active_award,"资源结算界面",0,300):
        label .findaward
        res = get_vector.find_xy(img_name.active_award)
        if res != None:
            click.click(res)
            goto .findaward
        else: goto.end
    else:goto.end

    label .end
    if click.auto_click(img_name.active_vector,"战斗胜利界面"):
        label .findend
        res = get_vector.find_xy(img_name.active_vector)
        if res != None:
            click.click(res)
            goto .findend
        else: goto.start
    else:goto.start


if __name__ == '__main__':
    while True:
        click.auto_click(img_name.active_start, "活动开始界面")
        click.auto_click(img_name.active_award,"资源结算界面",0,300)
        click.auto_click(img_name.active_vector,"战斗胜利界面")


