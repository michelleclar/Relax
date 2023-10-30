import mss
import core.base.cv as cv
import time
import numpy as np
import pyautogui
import cv2
from memory_profiler import profile
import numpy as np
# 平均帧数 140 内存 74mb cpu 峰值1.2 平均 0.4
now = lambda: time.time()


def main():
    times = []
    for i in range(100):
        start = now()
        win = pyautogui.getWindowsWithTitle("主账号")
        monitor = win[0].box
        time = now() - start
        times = time
    print(np.mean(times))
    # # monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
    # fpss = []
    # with mss.mss() as sct:
    #     # Part of the screen to capture
    #     # monitor = {"top": 40, "left": 0, "width": 800, "height": 640}
    #     static_time = now()
    #     while now() - static_time < 60:
    #         last_time = time.time()
    #
    #         # Get raw pixels from the screen, save it to a Numpy array
    #         img = sct.grab(monitor)
    #         img = np.array(img)
    #         # img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    #         # # 检查深度
    #         # if img.dtype != np.uint8 and img.dtype != np.float32:
    #         #     raise ValueError("img 的深度必须是 CV_8U 或 CV_32F")
    #         # template = cv2.imread(filename=f"./imgs/test_step2.png", flags=0)
    #         # # 检查类型
    #         # result = cv2.matchTemplate(image=img, templ=template, method=cv2.TM_CCOEFF_NORMED)
    #         # min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    #         # height, width = template.shape[::-1]
    #         # res = max_val - min_val
    #         # print(res)
    #         # pt = min_loc
    #         # pt = max_loc
    #         # cv2.rectangle(img, pt, (pt[0] + width, pt[1] + height), (0, 0, 225), 2)
    #         # 检查维度
    #         # if len(img.shape) > 2:
    #         #     raise ValueError("img 必须是二维图像")
    #         # Display the picture
    #         cv2.imshow("OpenCV/Numpy normal", img)
    #
    #         fps = 1 / (time.time() - last_time)
    #         fpss.append(fps)
    #         # print(f"fps: {1 / (time.time() - last_time)}")
    #
    #         # Press "q" to quit
    #         if cv2.waitKey(25) & 0xFF == ord("q"):
    #             cv2.destroyAllWindows()
    #             print(np.mean(fpss))
    #             break
    # print(np.mean(fpss))


if __name__ == '__main__':
    main()
