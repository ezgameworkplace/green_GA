'''
File:sdk_connection.py
Author:ezgameworkplace
Date:2022/11/27
'''
import time
from typing import Tuple

from green_GA.adb_connection import ADBConnection, Screen
from green_GA.client_socket import ClientSocket
from green_GA.commands import Commands
from green_GA.debug_log import debug_log
from green_GA.nox_console import NoxConsole
from green_GA.tree import UITree, ExactSearch, FuzzySearch, CaseSensitive


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


class UnitySDK(object):
    __slots__ = ['__ip', '__port', '__serial', '__sdk_port', '__tcp', '__adb_connection', '__socket', '__nox_console',
                 '__nox_name', '__encoding', '__timeout', '__update_connection', '__ui_delay', '__real_phone',
                 '__connected', '__ui_tree', '__width_dif', '__height_dif', '__reboot_limit', '__restart_limit',
                 '__package_name', '__package_main_activity_name', 'debug_mode']

    def __init__(self, ip: int or str, port: int or str, serial: str, real_phone: bool, package_name: str,
                 package_main_activity_name: str, sdk_port: int or str = '27019', nox_console_path: str = None,
                 nox_name: str = None, encoding: str = 'utf-8', timeout: int = 2, update_connection: int = 5,
                 ui_delay: float = 0.1, connect_at_init: bool = False, width_dif: float = 0, height_dif: float = 0,
                 reboot_limit=60, restart_limit=60, debug_mode=False):
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
        self.__tcp = (self.__port, self.__sdk_port)
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
        self.debug_mode = debug_mode
        if nox_console_path != None:
            self.__nox_console = NoxConsole(nox_console_path)
        if real_phone == False:
            if nox_console_path == None or nox_name == None:
                raise Exception('if using nox, must input NoxConsole.exe path and virtual box name')
        if connect_at_init == True:
            # FIXME socket运行多进程时候，会产生问题：需要在多进程的函数内再次connect，而init的connect不会生效
            self.connect()

    def __str__(self):
        return f'Current UnitySDK: \nip:{self.__ip}\nport:{self.__port}\nserial:{self.__serial}\n'

    @property
    def port(self) -> str:
        return self.__port

    @property
    def tcp(self):
        return self.__tcp

    @tcp.setter
    def tcp(self, v: Tuple[str, str]):
        self.__tcp = v

    @property
    def nox_name(self) -> str:
        return self.__nox_name

    @property
    def adb_connection(self) -> ADBConnection:
        return self.__adb_connection

    @property
    def serial(self) -> str:
        return self.__serial

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

    @package_name.setter
    def package_name(self, v: str):
        self.__package_name = v

    @property
    def package_main_activity_name(self):
        return self.__package_main_activity_name

    @package_main_activity_name.setter
    def package_main_activity_name(self, v: str):
        self.__package_main_activity_name = v

    @property
    def connected(self) -> bool:
        if self.adb_connection.check_adb_connection_ready(self.tcp,
                                                          self.__package_name) == True and self.socket.connected == True:
            self.__connected = True
        else:
            self.__connected = False
        return self.__connected

    @property
    def real_phone(self) -> bool:
        return self.__real_phone

    @property
    def device_screen(self) -> 'Screen':
        return self.adb_connection.get_device_cur_screen()

    @property
    def app_screen(self) -> 'Screen':
        return self.adb_connection.get_device_app_screen()

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
        self.__wait_reboot()

        if self.adb_connection.connected != True:
            raise Exception(f'device reboot failed after {self.__reboot_limit} seconds')

        self.__connect_tcp()

    def __wait_reboot(self) -> None:  # 加入重启的时间限制
        wait_time = self.__update_connection
        time_limit = self.__reboot_limit
        while self.adb_connection.connected != True and time_limit > 0:
            time_limit = time_limit - wait_time
            time.sleep(wait_time)

    def start_app(self, package_name: str, package_main_activity_name: str) -> None:
        self.__adb_connection.start_app(package_name, package_main_activity_name)

    def kill_app(self, package_name: str) -> None:
        self.__adb_connection.kill_app(package_name)

    def __restart_app(self, package_name: str, package_main_activity_name: str) -> None:
        try:
            self.kill_app(package_name)  # TODO 设备没启动的时候会报错的
            time.sleep(self.__update_connection)
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

    def __connect_tcp(self) -> None:
        self.__adb_connection.tcp_forward(self.__port, self.__sdk_port)

    def __connect_socket(self) -> None:
        self.__socket.client_socket = self.__socket.connect()

    def connect(self) -> None:
        self.__connect_tcp()
        self.__connect_socket()

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

    def restart_game(self, package_name: str = None, package_main_activity_name: str = None) -> None:
        if not package_name:
            package_name = self.package_name
        if not package_main_activity_name:
            package_main_activity_name = self.package_main_activity_name
        wait_time = self.__update_connection
        time_limit = self.__restart_limit
        self.restart_app(package_name, package_main_activity_name)
        # self.connect()
        while self.connected != True and time_limit > 0:
            if self.adb_connection.check_app_running(package_name) != True or self.adb_connection.check_app_focused(
                    package_name) != True:  # 保证app在运行
                self.restart_app(package_name, package_main_activity_name)
            if self.adb_connection.check_tcp_connected != True or self.socket.connected != True:  # 保证socket连接
                self.connect()
            time_limit = time_limit - wait_time
            time.sleep(wait_time)

    def dump_tree(self) -> dict:
        ret = self.send_command(Commands.DUMP_TREE)
        return ret

    def get_sdk_version(self) -> dict:
        ret = self.send_command(Commands.GET_VERSION, 1)
        return ret

    @debug_log
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

    def find_element_by_path_and_location(self, path: str, x: float, y: float,
                                          error: float = 50) -> 'Element' or None:
        # 存在同名element的时候，通过在屏幕上的坐标来选择，默认允许误差50
        elements = self.find_elements_by_path(path)

        for e in elements:
            bound = self.get_element_bound(e)

            x_error = round(abs(bound.x - x), 2)
            y_error = round(abs(bound.y - y), 2)

            if x_error <= error and y_error <= error:
                return e

        return None

    def find_element(self, path: str) -> Element or None:
        # FIXME 补全Element，需要修改sdk的C#代码, Commands.FIND_ELEMENTS只会返回名字和实例id，缺了txt/image等信息， 用FIND_ELEMENT_PATH可以补全这些信息，鬼知道为啥会有两个重复的功能
        # FIXME 加入参数visible，区分可见和不可见
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

    def __parse_node(self, node: dict) -> Element or None:
        if node is None:
            return None
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

    def wait(self, ui_path: str, exists=True, timeout=10, interval=0.25):
        """
        Wait until UI Element exists or gone
        """
        end_time = time.time() + timeout

        while time.time() < end_time:
            e = self.find_elements_by_path(ui_path)

            if bool(e) == exists:
                return True

            # Wait for a while before trying again
            time.sleep(interval)

        return False

    def wait_gone(self, ui_path: str, timeout: int = 10) -> bool:
        # 等待元素消失
        return self.wait(ui_path=ui_path, exists=False, timeout=timeout)

    def search_sibling_element_by_search_name_and_txt(self, search_name: str, search_ui_txt: str, sibling_name: str,
                                                      case=CaseSensitive) -> [dict]:
        return self.__parse_node(
            self.ui_tree.get_sibling_node_by_search_name_and_txt(search_name=search_name, search_ui_txt=search_ui_txt,
                                                                 sibling_name=sibling_name,
                                                                 case=case))

    def search_sibling_child_element_by_search_name_and_txt(self, search_name: str, search_ui_txt: str,
                                                            sibling_child_name: str,
                                                            case=CaseSensitive) -> [dict]:
        return self.__parse_node(
            self.ui_tree.get_sibling_child_by_search_name_and_txt(search_name=search_name, search_ui_txt=search_ui_txt,
                                                                  sibling_child_name=sibling_child_name,
                                                                  case=case))

    def search_closest_element_by_search_name_and_txt(self, search_name: str, search_ui_txt: str,
                                                      closest_name: str,
                                                      case=CaseSensitive) -> [dict]:
        # 子节点优先
        return self.__parse_node(
            self.ui_tree.get_closest_node(search_node_name=search_name, search_ui_txt=search_ui_txt,
                                          another_node_name=closest_name,
                                          case=case))

    def search_element_by_hash_code(self, hash_code: str):
        return self.__parse_node(self.ui_tree.get_node_by_hash(hash_code))

    def __call__(self, **kwargs):
        # TODO create a ui selector
        if "ui_path" in kwargs.keys():
            return self.find_elements_by_path(kwargs["ui_path"])
        else:
            raise Exception("must into ui_path as kwargs")

    def save_tree(self, save_path: str):
        self.ui_tree.save_tree(save_path)

    @property
    def hash_code_tree(self):
        return self.ui_tree.ui_tree_with_hash_code

# if __name__ == '__main__':
#     ip = 'localhost'
#     package_name = 'com.dts.freefireth'  # 游戏包名
#     package_main_activity_name = 'com.dts.freefireth.FFMainActivity'  # 游戏活动名
#
#     port1 = '60025'  # 本地端口1
#     serial1 = '127.0.0.1:62071'  # adb端口号1
#
#
#     phone1 = UnitySDK(ip, port1, serial1, real_phone=True, package_name=package_name,
#                       package_main_activity_name=package_main_activity_name, connect_at_init=False, debug_mode=True,
#                       ui_delay=0.1)
#
#     phone1.connect()
#     # phone1.save_tree("output5.xml")
#     #
#     # print(phone1.hash_code_tree)
#     e = phone1.search_element_by_hash_code("89cf1f1dcb10278c6afcf4c46763e9e58422786ea83238baea7f95d5d6627331")
#     phone1.click_element(e)
