from pymouse import Pymouse


m = Pymouse()

def move(point):
    m.move(point.x,point.y)


def scroll():
    """中键垂直滚动"""
    m.scroll(10,0)

def click(point):
    """1:左键，2:右键，3:中间"""
    m.click(point.x,point.y,1)

def drag(500,300):
    m.drag(point.x,point.y)

def screen_size():
    """获取屏幕大小"""
    return m.screen_size()

def position():
    """获取当前鼠标位置"""
    return m.position()


