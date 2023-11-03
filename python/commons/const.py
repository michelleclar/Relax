import yaml

execute_consts = {}
switch_consts = {}

def init():
    execute()


def execute():
    import python.core.base.log as log
    logger = log.get_logger()
    logger.info("正在读取配置")
    with open("../config.yml", "r") as f:
        ayml = yaml.load(f.read(), Loader=yaml.Loader)
        global execute_consts
        execute_consts = ayml["execute"]
        global switch_consts
        switch_consts = ayml["switch"]
    logger.info(f'配置内容为{ayml}')
# import yaml

# # 定义字典对象
# adict={
#   "name": "zhangsan",
#   "addr": "beijing",
#   "comp": ["comp1","comp2","comp3"],
#   "age": 18,
#   "love": {
#       "name": "xiaofang",
#       "age": 16
#   }
# }

# # 转换成yml字符串
# ayml=yaml.dump(adict)
# print(ayml)

# # 转换成yml字符串并写入文件
# with open("mydata.yml","w") as f:
#     yaml.dump(adict,f)
