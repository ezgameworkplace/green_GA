'''
File:debug_log.py
Author:ezgameworkplace
Date:2023/1/6
'''
import functools
import inspect
import logging
import os

from green_GA.commands import Commands


def get_command_name(command_value):
    for command_name, value in vars(Commands).items():
        if value == command_value:
            return command_name
    raise ValueError("Command value not found.")


def setup_logging(file_path, size_limit=10000000, count_lines=5000):
    if not os.path.exists(file_path):
        with open(file_path, 'w'):
            pass  # 文件不存在时创建一个空文件

    logging.basicConfig(filename=file_path,
                        level=logging.DEBUG,
                        format='%(asctime)s:%(levelname)s:%(message)s')

    size = os.path.getsize(file_path)  # in bytes
    if size > size_limit:
        with open(file_path, "r") as f:
            lines = f.readlines()
        del lines[count_lines:]
        with open(file_path, "w") as f:
            f.writelines(lines)

    return logging.getLogger()


def debug_log(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        sig = inspect.signature(func)
        bound_args = sig.bind(*args, **kwargs)
        self = bound_args.arguments.get('self')

        if self.debug_mode:
            if type(self).__name__ == 'UnitySDK':
                filename = self.port + ".log"
            else:
                raise Exception("打印log的装饰器只可以用于UnitySdk")

            file_path = os.path.join(os.getcwd(), filename)
            logger = setup_logging(file_path)
            logger.setLevel(logging.DEBUG)

            command = bound_args.arguments.get('command')
            if command is not None:
                logger.debug(f"The 'command' argument for {func.__name__} is: {get_command_name(command)}")

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
        else:
            return func(*args, **kwargs)

    return wrapper
