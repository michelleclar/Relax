import pyautogui
import ctypes
from pprint import pprint
import cv2
enumWindows = ctypes.windll.user32.EnumWindows
enumWindowsProc = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_int, ctypes.POINTER(ctypes.c_int))
getWindowText = ctypes.windll.user32.GetWindowTextW
getWindowTextLength = ctypes.windll.user32.GetWindowTextLengthW
isWindowVisible = ctypes.windll.user32.IsWindowVisible

def test():
    titles = []
    def foreach_window(hWnd, lParam):
        if isWindowVisible(hWnd):
            length = getWindowTextLength(hWnd)
            buff = ctypes.create_unicode_buffer(length + 1)
            getWindowText(hWnd, buff, length + 1)
            print(ctypes.windll.user32.IsWindowVisible(hWnd))
            titles.append((hWnd, buff.value))
        return True
    enumWindows(enumWindowsProc(foreach_window), 0)

    return titles

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



