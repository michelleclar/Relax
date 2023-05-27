from utils import get_vector, do_ocr, click

img_name = "jiejie_num"
# 保存匹配的实际图片
avg = get_xy(img_name,True)

text = do_ocr(img_name,True)
