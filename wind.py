import pyautogui
import ctypes
from pprint import pprint

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


def main():
    # active = pyautogui.getActiveWindow()
    # titles = pyautogui.getAllTitles()
    win1 = pyautogui.getWindowsWithTitle('主账号')
    # win2 = pyautogui.getWindowsWithTitle('副账号')

    # win2[0].visible()
    for win in win1:
        if win.isActive is False:
            win.restore()
            win.activate()
    rect = win1[0]._getWindowRect()
    print(rect.left != 0 and rect.top != 0 and rect.right != 0 and rect.bottom != 0)
    print(f'{win1[0].visible}')
    win1 = pyautogui.getWindowsWithTitle('主账号')
    print(f'{win1[0].isActive}')
    print('aaa')
    # print(pyautogui.getWindowsWithTitle)
    print(pyautogui.getActiveWindowTitle())
    wins = pyautogui.getAllWindows()
    print(pyautogui.getActiveWindow())
    # print(pyautogui.getActiveWindowTitle())


if __name__ == '__main__':
    main()
    # pprint(test())
   
