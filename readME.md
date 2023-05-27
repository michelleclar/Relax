# 写在最前

> 项目产生契机,因上班没时间玩游戏,写一个自动化游戏脚本

### 技术选型

| 库名          | 作用                                                     |
| :------------ | :------------------------------------------------------- |
| pyautogui     | 屏幕自动化控制库,用于获取屏幕截图等                      |
| opencv-python | OpenCV计算机视觉库的Python接口,用于图片处理和裁剪        |
| numpy         | Python科学计算库,用于矩阵运算和算法                      |
| Pillow        | 图像处理库,用于图片读取,处理和保存                       |
| pywin32       | Windows API封装库,用于Windows下系统交互和进程管理        |
| pytesseract   | Google Tesseract OCR引擎的Python包装器,用于图片文字识别  |
| paddlepaddle  | PaddlePaddle深度学习框架,提供深度学习功能                |
| paddleocr     | PaddlePaddle深度学习框架的OCR识别工具,支持90多国语言识别 |

> paddlepaddle是目前使用下来比ddddocr和pytesseract更好的ocr依赖库,[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md#2)
>
> 木项目导入的是cpu版本
>
> 本地CUDA版本为12高于paddlepaddle最高支持版,目前在跑AI绘画

### 项目环境搭建

```sh
pip install -r requirements.txt
```

> GPU版本需要安装CUDA
