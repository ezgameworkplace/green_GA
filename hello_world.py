'''
File:hello_world.py
Author:ezgameworkplace
Date:2022/12/9
'''
from multiprocessing import Process
from retrying import retry
import time
from ui_control import sdk_connection
import ingame

@retry(wait_fixed=2000)
def get_in_game(connection, package_name, package_main_activity_name):
    connection.reboot()
    connection.restart_game(package_name, package_main_activity_name)
    time.sleep(2)
    ingame.into_lobby(connection)


@retry(wait_fixed=2000)
def multi_devices(c1, c2, package_name, package_main_activity_name):
    p1 = Process(target=get_in_game, args=(c1,package_name, package_main_activity_name))
    p2 = Process(target=get_in_game, args=(c2,package_name, package_main_activity_name))
    p1.start()
    p2.start()
    print("device1's pid:", p1.ident)
    print("device2's pid:", p2.ident)
    p1.join()
    p2.join()

if __name__ == '__main__':
    # TODO 运行前，修改自定义参数
    ip = 'localhost'
    port1 = '60025' # 本地端口1
    port2 = '60026' # 本地端口2
    serial1 = '127.0.0.1:62040' # adb端口号1
    serial2 = '127.0.0.1:62041' # adb端口号2
    nox1 = '夜神模拟器1' # 模拟器名称1
    nox2 = '夜神模拟器2' # 模拟器名称2

    nox_console_path = r"D:\Program Files\Nox\bin\NoxConsole.exe" # 夜神NoxConsole路径

    package_name = '游戏包名' # 游戏包名
    package_main_activity_name = '游戏活动名' # 游戏活动名

    c1 = sdk_connection.UnitySDK(ip, port1, serial1, real_phone=False, nox_console_path=nox_console_path,
                                      nox_name=nox1)
    c2 = sdk_connection.UnitySDK(ip, port2, serial2, real_phone=False, nox_console_path=nox_console_path,
                                      nox_name=nox2)

    multi_devices(c1, c2, package_name, package_main_activity_name)