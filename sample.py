# -*- coding: utf-8 -*-
"""
File:sample.py
Author:ezgameworkplace
Date:2023/6/7
"""
from green_GA import UnitySDK

if __name__ == '__main__':
    # TODO 运行前，修改自定义参数
    ip = 'localhost'
    port = '60025'  # 本地端口1
    serial = '57439f5a'  # adb端口号1

    package_name = 'com.ezgamer'  # 游戏包名
    package_main_activity_name = 'com.unity3d.player.UnityPlayerActivity'  # 游戏活动名

    phone = UnitySDK(ip, port, serial, real_phone=True, package_name=package_name,
                     package_main_activity_name=package_main_activity_name, connect_at_init=False)

    phone.connect()

    # print(phone.restart_game())
    print(phone.ui_tree)
    attack_button = phone.search_element_by_name("Attack")[0]
    print("attack_button", attack_button)
    phone.click_element(attack_button)
