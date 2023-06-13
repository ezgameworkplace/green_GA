'''
File:hello_world.py
Author:ezgameworkplace
Date:2022/12/9
'''
import time
from multiprocessing import Process
from ui_control import UnitySDK

def get_in_game(connection, package_name, package_main_activity_name):
    connection.reboot()
    time.sleep(30)
    connection.restart_game(package_name, package_main_activity_name)
    time.sleep(2)
    connection.connect()


def multi_devices(c1, c2, package_name, package_main_activity_name):
    p1 = Process(target=get_in_game, args=(c1, package_name, package_main_activity_name))
    p2 = Process(target=get_in_game, args=(c2, package_name, package_main_activity_name))
    p1.start()
    p2.start()
    print("device1's pid:", p1.ident)
    print("device2's pid:", p2.ident)
    p1.join()
    p2.join()


if __name__ == '__main__':
    # TODO 运行前，修改自定义参数
    ip = 'localhost'
    port1 = '60025'  # 本地端口1
    port2 = '60026'  # 本地端口2
    serial1 = ''  # adb端口号1
    serial2 = ''  # adb端口号2
    nox1 = ''  # 模拟器名称1
    nox2 = ''  # 模拟器名称2

    nox_console_path = ''  # 夜神NoxConsole路径

    package_name = ''  # 游戏包名
    package_main_activity_name = ''  # 游戏活动名

    c1 = UnitySDK(ip, port1, serial1, real_phone=False, nox_console_path=nox_console_path, nox_name=nox1,
                  package_name=package_name, package_main_activity_name=package_main_activity_name,
                  connect_at_init=False)
    c2 = UnitySDK(ip, port2, serial2, real_phone=True, width_dif=100, package_name=package_name,
                  package_main_activity_name=package_main_activity_name, connect_at_init=False)

    multi_devices(c1, c2, package_name, package_main_activity_name)
