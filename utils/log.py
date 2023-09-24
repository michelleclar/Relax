import traceback
import loguru
import sys


def get_logger():
    logger = loguru.logger
    logger.remove()
    logger.add(sys.stdout,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{thread.name}</cyan> | <level>{message}</level>")
    return logger
def detail_error():
    return traceback.format_exc()