"""
日志操作
"""
from datetime import datetime
import traceback
import loguru
import sys


def get_logger():
    logger = loguru.logger
    logger.remove()
    logger.add(sys.stdout,
               format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{thread.name}</cyan> | <level>{message}</level>")
    # Define a custom log file name based on the current date and time
    log_file_path = f"../../logs/{datetime.now().strftime('%Y-%m-%d')}.log"

    # Add a file handler with rotation based on file size
    logger.add(log_file_path, rotation="100 MB", compression="zip", encoding="utf-8")

    return logger
def detail_error():
    return traceback.format_exc()