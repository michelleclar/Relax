```python

import cv2
import numpy as np


def click(picture_name):


# 读取图片
pic = cv2.imread(f'python/imgs/{picture_name}.png')
# 截取当前屏幕
screen = np.array(pyautogui.screenshot())
# 保存图片
cv2.imwrite('screenshot.png', screen)
# 转换颜色空间
pic = cv2.cvtColor(pic, cv2.COLOR_BGR2GRAY)
screen = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)
# 模板匹配
res = cv2.matchTemplate(screen, pic, cv2.TM_CCOEFF_NORMED)
# 查找最大值和坐标
min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
# 点击最大值坐标
pyautogui.moveTo(max_loc[0] + pic.shape[1] // 2, max_loc[1] + pic.shape[0] // 2)
pyautogui.click()

# 设置截图区域
screen_area = (0, 0, 800, 600)

# 游戏主循环
while True:
# 截取屏幕区域
screen = np.array(pyautogui.screenshot(region=screen_area))
# 转换为灰度图
gray = cv2.cvtColor(screen, cv2.COLOR_BGR2GRAY)

# 识别电脑中央的 '+' 号
plus_symbol = cv2.matchTemplate(gray, cv2.imread('plus_symbol.png', 0), cv2.TM_CCOEFF_NORMED)
location = np.where(plus_symbol >= 0.8)

# 如果找到 '+' 号,则点击该位置
if location[0].size > 0:
    click_location = (location[1][0] + screen_area[0], location[0][0] + screen_area[1])
    pyautogui.click(click_location)

# 0.5 秒后继续循环
cv2.waitKey(500)


class Game:


    def __init__(self):


    self.screen = None
self.player_pos = None


def get_screen(self):
    self.screen = pyautogui.screenshot()


def get_player_pos(self):
    # 使用OpenCV解析self.screen获取玩家位置
    self.player_pos = (x, y)


game = Game()
while True:
    game.get_screen()
game.get_player_pos()

# 使用AI算法计算下一步行动
action = ai_algo(game.screen, game.player_pos)

# 执行行动,如:
pyautogui.move(action[0], action[1])

import cv2


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
```

```python
from mss import mss
import cv2
import numpy as np
while True:
    img = mss().grab(monitor={"top":0,"left":0,"width":1920,"height":1080})
    img = np.array(img)
    cv2.imshow("img",img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        cv2.destroyAllWindows()
        break
```

### 队列处理图片截图
> 思想借鉴 后期可能会采用
```python
import mss
import mss.tools


def grab(queue: Queue) -> None:
    rect = {"top": 0, "left": 0, "width": 600, "height": 800}

    with mss.mss() as sct:
        for _ in range(1_000):
            queue.put(sct.grab(rect))

    # Tell the other worker to stop
    queue.put(None)


def save(queue: Queue) -> None:
    number = 0
    output = "screenshots/file_{}.png"
    to_png = mss.tools.to_png

    while "there are screenshots":
        img = queue.get()
        if img is None:
            break

        to_png(img.rgb, img.size, output=output.format(number))
        number += 1


if __name__ == "__main__":
    # The screenshots queue
    queue: Queue = Queue()

    # 2 processes: one for grabing and one for saving PNG files
    Process(target=grab, args=(queue,)).start()
    Process(target=save, args=(queue,)).start()
```