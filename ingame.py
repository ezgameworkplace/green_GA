'''
File:ingame.py
Author:ezgameworkplace
Date:2022/12/7
'''
import time


def click_debug(engine):
    path = r"/UIRoot/UILogin/LoginPanel/Debug/Sprite"
    elements = engine.find_elements_by_path(path)
    if elements != []:
        engine.click_element(elements[0])


def check_box(engine):
    path = "/UIRoot/UIDebugConsole/Commands/Table2/UIDebugConsoleToggle/Toggle/Checkmark"  # 关闭弹窗
    elements = engine.find_elements_by_path(path)
    e = elements[0]
    isCheckMark = engine.get_component_field(e, "UISprite", "alpha")
    if isCheckMark == "1":
        print("LobbyAutoTaskPop已经被勾选, 需要取消勾选，取消后游戏内不再弹出弹窗")
        engine.click_element(e)


def change_server(engine):
    path = r"/UIRoot/UIDebugConsole/Commands/Table2/UIDebugConsoleCommandItem/Name"  # 重名
    elements = engine.find_elements_by_path(path)
    if elements != []:
        for e in elements:
            if e.txt == 'Change Server':
                engine.click_element(e)


def change_server_rct02(engine):
    path = r"/UIRoot/UIDebugConsole/UIDebugConsoleOptionList/Scroll View/EasyList/ItemInstance(10-10)/OptionName"  # 重名 用模糊搜索txt #第一次进入才有
    elements = engine.find_elements_by_path(path)
    if elements != []:
        for e in elements:
            if e.txt == 'RCT02':
                engine.click_element(e)


def click_guest(engine):
    path = "/UIRoot/UILogin/LoginPanel/LoginBtns/Normal/BtnLoginGuest"
    elements = engine.find_elements_by_path(path)
    if elements != []:
        engine.click_element(elements[0])


def enter_lobby(engine):
    path = r"/UIRoot/UILogin/LoginPanel/BgStartGame"
    elements = engine.find_elements_by_path(path)
    if elements != []:
        engine.click_element(elements[0])


def start_game(engine):
    path = '/UIRoot/UILobbyNew/UILobbyNewRightBottom/RightBottom/TweenPosPanelRightBottom/soloPanel/BtnEnterGameSG'
    engine.click_element_by_path(path)


def into_lobby(engine):
    click_debug(engine)
    time.sleep(2)
    check_box(engine)
    time.sleep(2)
    change_server(engine)
    time.sleep(2)
    change_server_rct02(engine)
    time.sleep(2)
    click_guest(engine)
    time.sleep(2)
    enter_lobby(engine)
    time.sleep(10)
