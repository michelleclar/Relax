import cv2
import numpy
import subprocess


def _screenshot():
    pipe = subprocess.Popen("adb shell screencap -p", stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=True)
    image_bytes = pipe.stdout.read().replace(b'\r\n', b'\n')
    image = cv2.imdecode(numpy.fromstring(image_bytes, numpy.uint8), cv2.IMREAD_COLOR)
    return image


def scan_screenshot(prepared):
    screenshot = _screenshot()
    result = cv2.matchTemplate(screenshot, prepared, cv2.TM_CCORR_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
    return {'screenshot': screenshot, 'min_val': min_val, 'max_val': max_val, 'min_loc': min_loc, 'max_loc': max_loc}
