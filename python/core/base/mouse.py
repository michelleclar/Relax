import ctypes

MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_LEFTCLICK = MOUSEEVENTF_LEFTDOWN + MOUSEEVENTF_LEFTUP
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_RIGHTCLICK = MOUSEEVENTF_RIGHTDOWN + MOUSEEVENTF_RIGHTUP
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_MIDDLECLICK = MOUSEEVENTF_MIDDLEDOWN + MOUSEEVENTF_MIDDLEUP

kernel32 = ctypes.windll.kernel32
user32 = ctypes.windll.user32


def move(point):
    # 设置鼠标光标位置
    user32.SetCursorPos(point.x, point.y)


def click():
    user32.mouse_event(MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
    user32.mouse_event(MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)

    # 模拟键盘按下
    # key = 'a'
    # user32.keybd_event(ord(key), 0, 0, 0)
    # user32.keybd_event(ord(key), 0, KEYEVENTF_KEYUP, 0)


def lift_click(point):
    move(point=point)
    click()


if __name__ == '__main__':
    from python.core.base.structs import POINT
    import time

    # time.sleep(1)
    move(POINT(x=500, y=500))
    click()
