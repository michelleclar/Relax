# 写在最前

> 本项目核心为图像模板匹配 模板匹配技术使用的是opencv <br>
> 设计思想打算使用工作流来进行操作
> 目前工作流只有有向无环图这一种流程，因为本来打算是给阴阳师写的脚本，但在写的过程中发现可以进行解耦将他变成通用的游戏框架
> 关于防检测机制，并不打算进行完善，因为在写的过程中感觉没有意义，目前只加了随机点击，和随机延迟时间进行点击，后面打算进行剔除，
> 关于性能问题，本项目多线程进行操作我认为是避不开的，在协程和多线程上进行选择，我最终选择了线程池，因为关于上下文切换问题
> 这里是不存在的，而python协程他实际是单线程，在函数对象进行代码行切换而已，而这个切换我认为再快也会有时间的损失，所以不打算使用协程
> ocr 目前使用不是很多，而且好用的ocr他对于版本有些许限制，打算将他当插件抽取出来
> 图像识别 最终选择的是yolo8 因为机器学习并不通用 所以不打算将他加进核心中

### 技术选型

| 库名              | 作用                                    |
|:----------------|:--------------------------------------|
| ~~pyautogui~~   | 屏幕自动化控制库,用于获取屏幕截图等                    |
| opencv-python   | OpenCV计算机视觉库的Python接口,用于图片处理和裁剪       |
| numpy           | Python科学计算库,用于矩阵运算和算法                 |
| paddlepaddle    | PaddlePaddle深度学习框架,提供深度学习功能           |
| paddleocr       | PaddlePaddle深度学习框架的OCR识别工具,支持90多国语言识别 |
| gradio          | web界面                                 |
| loguru          | 日志框架                                  |
| memory_profiler | 内存分析工具                                |
| mss             | 高性能截图工具                               |
| pymouse         | 高性能操作鼠标库                              |
| pykeyboard      | 高性能键盘操作库                              |

>
paddlepaddle是目前使用下来比ddddocr和pytesseract更好的ocr依赖库,[PaddleOCR](https://github.com/PaddlePaddle/PaddleOCR/blob/release/2.6/doc/doc_ch/quickstart.md#2)
>
> 本项目导入的是cpu版本

### 项目环境

#### 依赖

> python(目前版本<=3.10即可)
> 主要影响因素在百度的ocr上 最高支持10后面打算将这个功能拆分出去 不能让他影响主项目

#### 实际开发环境

> conda 创建的虚拟环境 python版本使用 3.10
> linux 和 win 平台
> 开发工具 neovide pycharm

### 使用方式

> 1. ```sh
>    pip install -r requirements.txt -i https://mirrors.tuna.tsinghua.edu.cn/pypi/web/simple
>    ```
>
> 2. 编写[config.ymal](./doc/config.md) 进行参数设置
>
> 3. 编写[task.ymal](./doc/task.md) 进行任务设置
>
> 4. 运行app.py

### 注意事项

> 百度OCR
> GPU版本需要安装CUDA
> 官方推荐是CUDA 10 到11.1 太低了 所以不打算采用GPU
> 等以后出一个CUDA管理工具才会考虑
> 如要使用GPU版本 安装paddlepaddle-gpu
