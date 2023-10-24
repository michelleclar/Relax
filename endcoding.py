import codecs


def main():
    # 打开文件
    with open("config.yml", "r", encoding='utf-8') as f:
        # 读取文件内容
        content = f.read()
        # 解码文件内容
        content = content.decode("gbk")
        # 编码为 UTF-8
        content = content.encode("utf-8")

    # 写入文件
    with open("file.txt", "w") as f:
        f.write(content)


if __name__ == '__main__':
    main()
