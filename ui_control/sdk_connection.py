'''
File:sdk_connection.py
Author:ezgameworkplace
Date:2022/11/27
'''
import time
from ui_control.adb_connection import Screen, ADBConnection
from ui_control.client_socket import ClientSocket
from ui_control.nox_console import NoxConsole
from ui_control.tree import UITree, ExactSearch, FuzzySearch, CaseSensitive, CaseInsensitive


class ElementBound(object):

    def __init__(self, x, y, width, height, visible=True, existed=True):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.visible = visible
        self.existed = existed

    def __str__(self):
        return "point({0},{1}) width = {2} height = {3},visible={4}".format(self.x, self.y, self.width, self.height,
                                                                            self.visible, self.existed)

    def __repr__(self):
        return self.__str__()

    def get_center_point(self):
        return self.x + self.width / 2, self.y + self.height / 2


class WorldBound(object):

    def __init__(self, _id, _existed):
        self.id = _id
        self.existed = _existed

        # center_x,center_y,center_z,the center of the bounding box
        self.center_x = 0
        self.center_y = 0
        self.center_z = 0

        # the extents of the box,
        self.extents_x = 0
        self.extents_y = 0
        self.extents_z = 0

    def __str__(self):
        return "center = ({0},{1},{2}) extents = ({3},{4},{5})".format(self.center_x, self.center_y, self.center_z,
                                                                       self.extents_x, self.extents_y, self.extents_z)


class Element(object):
    __slots__ = ['__object_name', '__instance', '_components', '_txt', '_img']

    def __init__(self, object_name, instance, components=None, txt=None, img=None):
        self.__object_name = object_name
        self.__instance = instance
        self._components = components
        self._txt = txt
        self._img = img

    @property
    def object_name(self):
        return self.__object_name

    @property
    def instance(self):
        if isinstance(self.__instance, int):
            return self.__instance
        elif isinstance(self.__instance, str):
            return int(self.__instance)
        else:
            raise Exception('instance must be int')

    @property
    def components(self):
        return self._components

    @components.setter
    def components(self, value):
        self._components = value

    @property
    def txt(self):
        return self._txt

    @txt.setter
    def txt(self, value):
        self._txt = value

    @property
    def img(self):
        return self._img

    @img.setter
    def img(self, value):
        self._img = value

    def __str__(self):
        return f"GameObject {self.object_name} Instance = {self.instance} Components = {self.components} Txt = {self._txt} Img = {self._img}"

    def __eq__(self, element):
        return hasattr(element, 'instance') and self.__instance == element.instance

    def __ne__(self, element):
        return not self.__eq__(element)

    def __repr__(self):
        return f'<{type(self).__module__}.{type(self).__name__} (object_name="{self.object_name}", instance="{self.instance}", components="{self.components}", txt ="{self.txt}", img ="{self.img}")>'


class Commands(object):
    GET_VERSION = 100  # 获取版本号
    FIND_ELEMENTS = 101  # 查找节点
    FIND_ELEMENT_PATH = 102  # 模糊查找
    GET_ELEMENTS_BOUND = 103  # 获取节点的位置信息
    GET_ELEMENT_WORLD_BOUND = 104  # 获取节点的世界坐标
    GET_UI_INTERACT_STATUS = 105  # 获取游戏的可点击信息，包括scene、可点击节点，及位置信息
    GET_CURRENT_SCENE = 106  # 获取Unity的Scene名称
    GET_ELEMENT_TEXT = 107  # 获取节点的文字内容
    GET_ELEMENT_IMAGE = 108  # 获取节点的图片名称
    GET_REGISTERED_HANDLERS = 109  # 获取注册的函数的名称
    CALL_REGISTER_HANDLER = 110  # 调用注册的函数
    SET_INPUT_TEXT = 111  # input控件更换文字信息
    GET_OBJECT_FIELD = 112  # 通过反射获取gameobject中component的属性值
    FIND_ELEMENTS_COMPONENT = 113  # 获取所有包含改组件的gameobject
    SET_CAMERA_NAME = 114  # 设置渲染的最佳的Camera
    GET_COMPONENT_METHODS = 115  # 反射获取组件上的方法
    CALL_COMPONENT_MOTHOD = 116  # 通过反射调用组件的函数
    LOAD_TEST_LIB = 117  # 初始化testlib服务

    PRC_SET_METHOD = 118  # 注册python端的方法
    RPC_METHOD = 119  # 游戏内的接口可调用，python端的方法

    #######################/
    HANDLE_TOUCH_EVENTS = 200  # 发送down move up

    DUMP_TREE = 300


class UnitySDK(object):
    __slots__ = ['__ip', '__port', '__serial', '__sdk_port', '__adb_connection', '__socket', '__nox_console',
                 '__nox_name', '__encoding', '__timeout', '__update_connection', '__ui_delay', '__real_phone',
                 '__connected', '__ui_tree', '__width_dif', '__height_dif', '__reboot_limit', '__restart_limit',
                 '__package_name', '__package_main_activity_name']

    def __init__(self, ip: int or str, port: int or str, serial: str, real_phone: bool, package_name: str,
                 package_main_activity_name: str, sdk_port: int or str = '27019', nox_console_path: str = None,
                 nox_name: str = None, encoding: str = 'utf-8', timeout: int = 2, update_connection: int = 5,
                 ui_delay: int = 0.1, connect_at_init: bool = False, width_dif: float = 0, height_dif: float = 0,
                 reboot_limit=60, restart_limit=60):
        self.__ip = ip
        self.__port = port
        self.__serial = serial
        self.__sdk_port = sdk_port
        self.__nox_name = nox_name
        self.__encoding = encoding
        self.__timeout = timeout
        self.__update_connection = update_connection
        self.__ui_delay = ui_delay
        self.__real_phone = real_phone
        self.__connected = False
        self.__adb_connection = ADBConnection(serial=self.__serial, encoding=self.__encoding, local_port=self.__port,
                                              device_port=self.__sdk_port)
        self.__socket = ClientSocket(ip=self.__ip, port=self.__port, encoding=self.__encoding, timeout=self.__timeout)
        self.__ui_tree = UITree()
        self.__width_dif = width_dif
        self.__height_dif = height_dif
        self.__reboot_limit = reboot_limit
        self.__restart_limit = restart_limit
        self.__package_name = package_name
        self.__package_main_activity_name = package_main_activity_name
        if nox_console_path != None:
            self.__nox_console = NoxConsole(nox_console_path)
        if real_phone == False:
            if nox_console_path == None or nox_name == None:
                raise Exception('if using nox, must input NoxConsole.exe path and virtual box name')
        if connect_at_init == True:
            # FIXME socket运行多进程时候，会产生问题：需要在多进程的函数内再次connect，而init的connect不会生效
            self.connect()

    def __str__(self):
        return f'ip:{self.__ip}\nport:{self.__port}\nserial:{self.__serial}\nadb_connection:{self.__adb_connection}\nsocket:{self.__socket}\nnox_console:{self.__nox_console}'

    @property
    def adb_connection(self) -> ADBConnection:
        return self.__adb_connection

    @property
    def socket(self) -> ClientSocket:
        return self.__socket

    @property
    def width_dif(self) -> float:
        return self.__width_dif

    @property
    def height_dif(self) -> float:
        return self.__height_dif

    def get_ui_tree(self) -> str:
        return self.__ui_tree.xml_tree

    def __set_ui_tree(self) -> dict:
        return self.dump_tree()['xml']

    def set_ui_tree(self) -> None:
        self.__ui_tree.xml_tree = self.__set_ui_tree()

    @property
    def ui_tree(self) -> UITree:
        try:
            self.set_ui_tree()
        except Exception as e:
            raise Exception(f"err:{e}, can't access ui tree")
        return self.__ui_tree

    @property
    def package_name(self):
        return self.__package_name

    @property
    def package_main_activity_name(self):
        return self.__package_main_activity_name

    @property
    def connected(self) -> bool:
        if self.adb_connection.check_adb_connection_ready(
                self.__package_name) == True and self.socket.connected == True:
            self.__connected = True
        else:
            self.__connected = False
        return self.__connected

    @property
    def real_phone(self) -> bool:
        return self.__real_phone

    def __reboot(self) -> None:
        # FIXME 某些手机启动后会显示adb已连接，activity还未准备，造成无法重启app，需要加入等待时间
        if self.__real_phone == True:
            self.adb_connection.reboot()
        elif self.__real_phone == False:
            # TODO 判断一下是否存在
            self.__nox_console.launch(self.__nox_name)
            self.__nox_console.reboot(self.__nox_name)
        else:
            raise Exception('input bool for real phone, for False only support nox_console')

    def reboot(self) -> None:
        self.__reboot()
        wait_time = self.__update_connection
        time_limit = self.__reboot_limit
        while self.adb_connection.connected != True and time_limit > 0:  # 加入时间限制
            time_limit = time_limit - wait_time
            time.sleep(wait_time)
        if self.adb_connection.connected != True:
            raise Exception(f'device reboot failed after {self.__reboot_limit} seconds')

    def start_app(self, package_name: str, package_main_activity_name: str) -> None:
        self.__adb_connection.start_app(package_name, package_main_activity_name)

    def kill_app(self, package_name: str) -> None:
        self.__adb_connection.kill_app(package_name)

    def __restart_app(self, package_name: str, package_main_activity_name: str) -> None:
        try:
            self.kill_app(package_name)
            self.start_app(package_name, package_main_activity_name)
        except:
            self.start_app(package_name, package_main_activity_name)

    def restart_app(self, package_name: str, package_main_activity_name: str) -> None:
        self.__restart_app(package_name, package_main_activity_name)
        wait_time = self.__update_connection
        time_limit = self.__restart_limit
        while self.adb_connection.check_app_running(package_name) != True and time_limit > 0:
            time_limit = time_limit - wait_time
            time.sleep(wait_time)

    def __connect(self) -> None:
        self.__adb_connection.tcp_forward(self.__port, self.__sdk_port)
        self.__socket.client_socket = self.__socket.reconnect_socket()

    def connect(self) -> None:
        self.__connect()

    def __disconnect(self) -> None:
        try:
            self.__adb_connection.tcp_remove(self.__port)
        except:
            pass
        try:
            self.__socket.disconnect()
        except:
            pass

    def disconnect(self) -> None:
        self.__disconnect()

    def restart_game(self, package_name: str, package_main_activity_name: str) -> None:
        wait_time = self.__update_connection
        time_limit = self.__restart_limit
        self.restart_app(package_name, package_main_activity_name)
        # self.connect()
        while self.connected != True and time_limit > 0:
            if self.adb_connection.check_app_running(package_name) != True or self.adb_connection.check_app_focused(
                    package_name) != True:  # 保证app在运行
                self.restart_app(package_name, package_main_activity_name)
            if self.adb_connection.tcp_connected != True or self.socket.connected != True:  # 保证socket连接
                self.connect()
            time_limit = time_limit - wait_time
            time.sleep(wait_time)

    def dump_tree(self) -> dict:
        ret = self.send_command(Commands.DUMP_TREE)
        return ret

    def get_sdk_version(self) -> dict:
        ret = self.send_command(Commands.GET_VERSION, 1)
        return ret

    def __send_command(self, command: int, param: str or int = None) -> dict:
        return self.__socket.send_command(command, param)

    def send_command(self, command: int, param: str or int = None) -> dict:
        if self.__ui_delay > 0:
            time.sleep(self.__ui_delay)
        ret = self.__send_command(command, param)
        if ret['status'] != 0:
            raise Exception('The remote server returned an error.')
        return ret['data']

    def _parse_path(self, path: str) -> [dict]:
        # 分割path
        nodes = path.split("/")
        parsed_nodes = [{"name": node} for node in nodes if node]
        if parsed_nodes == []:
            raise Exception("invalid path")
        return parsed_nodes

    def find_elements_by_path(self, path: str) -> [Element]:
        # 根据path找到元素,path可以不全,补全path,同名返回所有
        parsed_nodes = self._parse_path(path)
        elements = self.send_command(Commands.FIND_ELEMENT_PATH, parsed_nodes)
        return [self.search_element_by_id(e["instance"]) for e in elements]

    def find_element(self, path: str) -> Element or None:
        # FIXME 补全Element，需要修改sdk的C#代码
        # 根据path找到元素,path可以不全,不补全path,同名只返回第一个
        ret = self.send_command(Commands.FIND_ELEMENTS, [path])
        if ret:
            ret = ret[0]
            if ret["instance"] == -1:
                return None
            else:
                return Element(ret["name"], ret["instance"])
        else:
            return None

    def find_elements_by_component(self, name: str) -> [Element]:
        # FIXME 根据component的名字搜索elements，暂时不可用，需要查看c#脚本
        ret = self.send_command(Commands.FIND_ELEMENTS_COMPONENT, [name])
        if ret is None:
            return []
        else:
            elements = [Element(e["name"], e["instance"]) for e in ret]
            return elements

    def get_element_bound(self, element: Element) -> ElementBound or None:
        # 获取元素的bound
        ret = self.send_command(Commands.GET_ELEMENTS_BOUND, [element.instance])
        if ret:
            ret = ret[0]
            return ElementBound(ret["x"], ret["y"], ret["width"], ret["height"], ret["visible"], ret["existed"])
        return None

    def get_all_elements(self) -> [Element]:
        ret = [Element(node.attrib["name"], node.attrib["id"], node.attrib["components"]) for node in
               self.ui_tree.get_all_nodes()]
        return ret

    def __parse_node(self, node: dict) -> Element:
        custom = ['name', 'id', 'components', 'txt', 'img']
        e = {k: None if k not in node.keys() else node[k] for k in custom}
        return Element(object_name=e["name"], instance=e["id"], components=e["components"], txt=e["txt"], img=e["img"])

    def search_element_by_id(self, id) -> Element:
        ret = [self.__parse_node(node) for node in
               self.ui_tree.get_nodes_by_attr_value('id', id, mode=ExactSearch)]
        if ret != []:
            return ret[0]

    def search_element_by_name(self, search: str, mode=FuzzySearch, case=CaseSensitive) -> [Element]:
        # 通过dump_tree根据path返回匹配的元素(类似find_elements_by_path,但是不补齐path)
        return [self.__parse_node(node) for node in self.ui_tree.get_nodes_by_attr_value('name', search, mode, case)]

    def search_element_by_components(self, search: str, mode=FuzzySearch, case=CaseSensitive) -> [Element]:
        # 通过dump_tree根据component返回匹配的元素
        return [self.__parse_node(node) for node in
                self.ui_tree.get_nodes_by_attr_value('components', search, mode, case)]

    def search_element_by_txt(self, search: str, mode=FuzzySearch, case=CaseSensitive) -> [Element]:
        # 通过dump_tree根据txt返回匹配的元素
        return [self.__parse_node(node) for node in self.ui_tree.get_nodes_by_attr_value('txt', search, mode, case)]

    def search_element_by_img(self, search: str, mode=FuzzySearch, case=CaseSensitive) -> [Element]:
        # 通过dump_tree根据img返回匹配的元素
        return [self.__parse_node(node) for node in self.ui_tree.get_nodes_by_attr_value('img', search, mode, case)]

    def __point_in_bound(self, x: float, y: float, element: Element) -> bool:
        element_bound = self.get_element_bound(element)
        if element_bound.x <= x <= element_bound.x + element_bound.width and element_bound.y <= y <= element_bound.y + element_bound.height:
            return True
        else:
            return False

    def search_elements_by_point(self, x: float, y: float) -> [Element]:
        elements = self.get_all_elements()
        return [e for e in elements if self.__point_in_bound(x, y, e) == True]

    def get_scene(self) -> dict:
        ret = self.send_command(Commands.GET_CURRENT_SCENE)
        return ret

    def get_element_text(self, element: Element) -> Element.txt:
        # FIXME Commands.GET_ELEMENT_TEXT在SDK不同步，需要修复C#代码
        # ret = self.send_command(Commands.GET_ELEMENT_TEXT, element.instance)
        return element.txt

    def get_element_image(self, element: Element) -> Element.img:
        # FIXME 同上
        # ret = self.send_command(Commands.GET_ELEMENT_IMAGE, element.instance)
        return element.img

    def get_existed_elements(self, elements: [Element]) -> [Element] or []:
        # 获取存在的元素
        elements_info = [self.send_command(Commands.GET_ELEMENTS_BOUND, [e.instance]) for e in elements]
        ret = [ei for ei in elements_info if ei[0]["existed"] == True]
        return ret

    def get_non_existed_elements(self, elements: [Element]) -> [Element] or []:
        # 获取不存在的元素
        elements_info = [self.send_command(Commands.GET_ELEMENTS_BOUND, [e.instance]) for e in elements]
        ret = [ei for ei in elements_info if ei[0]["existed"] == False]
        return ret

    def get_touchable_elements(self, params: str = None) -> [Element] or []:
        # 获取可以点击的元素
        ret = self.send_command(Commands.GET_UI_INTERACT_STATUS, params)
        if ret is None:
            return []
        else:
            ret_elements = ret['elements']
            elements = [Element(e['name'], e['instanceid']) for e in ret_elements]
            return elements

    def get_touchable_elements_bound(self, params: str = None) -> [ElementBound] or []:
        ret = self.send_command(Commands.GET_UI_INTERACT_STATUS, params)
        if ret is None:
            return []
        else:
            ret_elements_bound = ret['elements']
            elements_bound = [
                ElementBound(e['bound']['x'], e['bound']['y'], e['bound']['fWidth'], e['bound']['fHeight']) for e in
                ret_elements_bound]
            return elements_bound

    def set_input(self, element: Element, text: str) -> dict:
        ret = self.send_command(Commands.SET_INPUT_TEXT, {"instance": element.instance, "content": text})
        return ret

    def get_element_world_bound(self, elements: [Element]) -> [WorldBound]:
        # 获取元素的世界坐标
        if isinstance(elements, Element):
            elements = [elements]
        req = [e.instance for e in elements]
        ret = self.send_command(Commands.GET_ELEMENT_WORLD_BOUND, req)
        world_bounds = []
        for res in ret:
            world_bound = WorldBound(res["id"], res["existed"])
            if world_bound.existed:
                world_bound.center_x = res["centerX"]
                world_bound.center_y = res["centerY"]
                world_bound.center_z = res["centerZ"]
                world_bound.extents_x = res["extentsX"]
                world_bound.extents_y = res["extentsY"]
                world_bound.extents_z = res["extentsZ"]
                world_bounds.append(world_bound)
        return world_bounds

    def get_component_field(self, element: Element, component: str, attribute: str) -> dict:
        # 通过元素的id，component，attribute name获取attribute值
        ret = self.send_command(Commands.GET_OBJECT_FIELD,
                                {"instance": element.instance, "comopentName": component,
                                 "attributeName": attribute})
        return ret

    def set_camera(self, camera: str) -> dict:
        ret = self.send_command(Commands.SET_CAMERA_NAME, [camera])
        return ret

    def get_component_methods(self, element: Element, component: str) -> dict:
        # 通过元素的id，component获取component的method
        # 返回方法的【'methodName', 'returnType', 'parameterTypes'】
        ret = self.send_command(Commands.GET_COMPONENT_METHODS,
                                {"instance": element.instance, "comopentName": component})
        return ret

    def call_component_method(self, element: Element, component: str, method: str, params: str or None) -> dict:
        # 调用component的方法 TODO 只支持get方法，其他需要c#支持
        ret = self.send_command(Commands.CALL_COMPONENT_MOTHOD,
                                {"instance": element.instance, "comopentName": component,
                                 "methodName": method, "parameters": params})
        return ret

    def get_registered_handlers(self) -> dict:
        ret = self.send_command(Commands.GET_REGISTERED_HANDLERS)
        return ret

    def call_registered_handler(self, name: str, args: str) -> dict:
        ret = self.send_command(Commands.CALL_REGISTER_HANDLER, {"name": name, "args": args})
        return ret

    def game_script_init(self, path):
        # TODO 运行加入的c#脚本
        pass

    def register_game_callback(self, name, func):
        # TODO 回调函数
        pass

    def __click_position(self, x, y):
        self.adb_connection.click_position(x, y)

    def click_position(self, x, y):
        x = x + self.width_dif
        y = y + self.height_dif
        self.__click_position(x, y)

    def __press_position(self, x, y, duration):
        self.adb_connection.press_position(x, y, duration)

    def press_position(self, x, y, duration):
        x = x + self.width_dif
        y = y + self.height_dif
        self.__press_position(x, y, duration)

    def __swipe_position(self, x1, y1, x2, y2, duration: int = 500):
        self.adb_connection.swipe_position(x1, y1, x2, y2, duration)

    def swipe_position(self, x1, y1, x2, y2, duration: int = 500, press_duration: int = 50):
        self.press_position(x1, y1, press_duration)  # 需要按住再拖动
        x1 = x1 + self.width_dif
        y1 = y1 + self.height_dif
        x2 = x2 + self.width_dif
        y2 = y2 + self.height_dif
        self.__swipe_position(x1, y1, x2, y2, duration)

    def click_element(self, element: Element) -> int(0):
        element_bound = self.get_element_bound(element)
        x, y = element_bound.get_center_point()
        self.click_position(x, y)
        return 0

    def click_element_by_path(self, src: str) -> int(0):
        element = self.find_element(src)
        return self.click_element(element)

    def press_element(self, element: Element, duration: int) -> int(0):
        element_bound = self.get_element_bound(element)
        x, y = element_bound.get_center_point()
        self.press_position(x, y, duration)
        return 0

    def press_element_by_path(self, src: str, duration: int) -> int(0):
        element = self.find_element(src)
        return self.press_element(element, duration)

    def swipe_element(self, src_element: Element, dst_element: Element, duration: int = 500,
                      press_duration: int = 50) -> int(0):
        src_element_bound = self.get_element_bound(src_element)
        dst_element_bound = self.get_element_bound(dst_element)
        src_x, src_y = src_element_bound.get_center_point()
        dst_x, dst_y = dst_element_bound.get_center_point()
        self.swipe_position(src_x, src_y, dst_x, dst_y, duration, press_duration)
        return 0

    def swipe_element_by_path(self, src: str, dst: str, duration: int = 500) -> int(0):
        src_element = self.find_element(src)
        dst_element = self.find_element(dst)
        return self.swipe_element(src_element, dst_element, duration)
