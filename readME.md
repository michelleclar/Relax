# 写在最前

> 项目产生契机,因上班没时间玩游戏,写一个自动化游戏脚本

### 技术选型

| 库名            | 作用                                    |
|:--------------|:--------------------------------------|
| pyautogui     | 屏幕自动化控制库,用于获取屏幕截图等                    |
| opencv-python | OpenCV计算机视觉库的Python接口,用于图片处理和裁剪       |
| numpy         | Python科学计算库,用于矩阵运算和算法                 |
| Pillow        | 图像处理库,用于图片读取,处理和保存                    |
| paddlepaddle  | PaddlePaddle深度学习框架,提供深度学习功能           |
| paddleocr     | PaddlePaddle深度学习框架的OCR识别工具,支持90多国语言识别 |
| gradio        | web界面                                 |
| loguru        | 日志框架                                  |

> paddlepaddle是目前使用下来比ddddocr和pytesseract更好的ocr依赖库,[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md#2)
>
> 本项目导入的是cpu版本

### 项目环境搭建

> python版本 3.8
> 3.10测试也可以安装依赖
> 主要影响因素在百度的ocr上 后面打算将这个功能拆分出去 不能让他影响主项目

```sh
pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
```

> GPU版本需要安装CUDA
> 官方推荐是CUDA 10 到11.1 太低了 所以不打算采用GPU
> 等以后出一个CUDA管理工具才会考虑
> paddlepaddle-gpu
