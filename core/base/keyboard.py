from pykeyboard import Pykeyboard

k = Pykeyboard()

def type_string():
    k.type_string('Hello')

def press_key():
    """按下按键"""
    k.press_key('H')

def release_key():
    """释放按键"""
    k.release_key('H')

def tap_key():
    """按下并释放"""
    k.tap_key('H')
    # n 按下次数 间隔时间 秒
    k.tap_key('1',n=2,interval=5)


# alt
k.alt_key
# tap
k.tap_key
# F5
k.function_keys[5]
# Home键
k.numpad_key['Home']
# 数字5
k.numpad_key[5]
