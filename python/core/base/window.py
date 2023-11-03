import ctypes
from ctypes import wintypes as w
from python.core.base.structs import POINT, BOX

SW_MINIMIZE = 6
SW_MAXIMIZE = 3
SW_HIDE = 0
SW_SHOW = 5
SW_RESTORE = 9


def errcheck(result, func, args):
    if result is None or result == 0:
        raise ctypes.WinError(ctypes.get_last_error())
    return result


# wintypes.RECT doesn't know how to display itself,
# so make a subclass that does.
class Rect(w.RECT):
    def __repr__(self):
        return f'Rect(left={self.left},top={self.top},right={self.right},bottom={self.bottom})'


user32 = ctypes.WinDLL('user32', use_last_error=True)
# user32.FindWindowW.argtypes = w.LPCWSTR, w.LPCWSTR
# user32.FindWindowW.restype = w.HWND
# user32.GetWindowRect.argtypes = w.HWND, ctypes.POINTER(Rect)
# user32.GetWindowRect.restype = w.BOOL
# user32.GetWindowRect.errcheck = errcheck
# user32.ShowWindow
# user32.SetForegroundWindow


def get_rect_with_title(title: str):
    hwnd = user32.FindWindowW(None, title)
    if hwnd:
        rect = Rect()
        user32.GetWindowRect(hwnd, ctypes.byref(rect))
        return rect, hwnd
    else:
        print('window not found')


def cursor():
    """得到当前鼠标坐标"""
    cursor = POINT()
    user32.GetCursorPos(ctypes.byref(cursor))
    return POINT(x=cursor.x, y=cursor.y)


def resolution():
    """返回当前屏幕的宽高"""
    return BOX(width=user32.GetSystemMetrics(0), height=user32.GetSystemMetrics(1))


def restore(hWnd):
    user32.ShowWindow(hWnd, SW_RESTORE)


def activate(hWnd):
    user32.SetForegroundWindow(hWnd)

if __name__ == '__main__':
    rect , hwnd = get_rect_with_title('主账号')
    restore(hwnd)
    activate(hwnd)
