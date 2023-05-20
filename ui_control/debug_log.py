'''
File:debug_log.py
Author:ezgameworkplace
Date:2023/1/6
'''
import logging
import logging.handlers
import os


# def debug_log(func):
#     logging.basicConfig(filename="debug.log",
#                         level=logging.DEBUG,
#                         format='%(asctime)s:%(levelname)s:%(message)s')
#     logger = logging.getLogger(func.__name__)
#     logger.setLevel(logging.DEBUG)
#
#     def wrapper(*args, **kwargs):
#         logger.debug(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")
#         result = func(*args, **kwargs)
#         logger.debug(f"{func.__name__} returned: {result}")
#         return result
#
#     return wrapper

def debug_log(func, size_limit=10000000, count_lines=5000):
    def wrapper(*args, **kwargs):
        if isinstance(args[0], type(args[0])):
            instance = args[0]
            filename = instance.port + ".log"
        else:
            raise Exception("打印log需要正确的UnitySdk.port名称")
        get_dir_path = lambda: os.getcwd()
        dir_path = get_dir_path()
        file_path = os.path.join(dir_path, filename)
        if not os.path.exists(file_path):
            with open(file_path, 'w'):
                pass  # 文件不存在时创建一个空文件
        logging.basicConfig(filename=file_path,
                            level=logging.DEBUG,
                            format='%(asctime)s:%(levelname)s:%(message)s')
        logger = logging.getLogger(func.__name__)
        logger.setLevel(logging.DEBUG)

        # 如果太大，进行清除
        size = os.path.getsize(file_path)  # in bytes
        if size > size_limit:
            with open(file_path, "r") as f:
                lines = f.readlines()
            del lines[count_lines:]
            with open(file_path, "w") as f:
                f.writelines(lines)

        logger.debug(f"Calling {func.__name__} with args: {args} and kwargs: {kwargs}")
        try:
            result = func(*args, **kwargs)
            status = 1
        except Exception as e:
            logger.exception(f"An error occurred while executing {func.__name__}: {e}")
            result = None
            status = 0

        logger.debug(f"{func.__name__} returned status: {status}")
        return result

    return wrapper