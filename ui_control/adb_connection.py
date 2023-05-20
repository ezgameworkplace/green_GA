'''
File:adb_connection.py
Author:ezgameworkplace
Date:2022/11/25
'''
import subprocess


class Screen():
    def __init__(self, width, height):
        self.__width = int(width)
        self.__height = int(height)

    @property
    def width(self):
        return self.__width

    @property
    def height(self):
        return self.__height

    def __str__(self):
        return f'this is a screen with width={self.width}, height={self.height}'


class ADBConnection():
    SingleDevice = 0
    MultipleDevice = 1

    __slots__ = ['__serial', '__encoding', '__connected', '__local_port', '__device_port']

    def __init__(self, serial, encoding='utf-8', local_port=None, device_port=None):
        self.__serial = serial
        self.__encoding = encoding
        self.__connected = False
        self.__local_port = local_port
        self.__device_port = device_port

    def __str__(self):
        return f'adb connection info:\nserial:{self.__serial}'

    @property
    def serial(self):
        return self.__serial

    @property
    def device_port(self):
        return self.__device_port

    def __connected_devices(self):
        adb_cmd = f'devices'
        return self.run_adb_cmd(adb_cmd, self.SingleDevice)

    def connected_devices(self):
        devices_header = 'List of devices attached'
        devices_connected = 'device'
        ret = self.__connected_devices()
        if isinstance(ret, tuple): # 有时候是tuple 有时候是str
            ret = ret[0]
        lines = [line for line in ret.split('\n') if line != '' and line != devices_header]
        tabs = [line.split('\t') for line in lines]
        devices_serial = [tab[0] for tab in tabs if tab[1] == devices_connected]
        return devices_serial

    @property
    def connected(self):
        try:
            if self.serial in self.connected_devices():
                self.__connected = True
            else:
                self.__connected = False
        except:
            self.__connected = False
        return self.__connected

    def __run_cmd(self, cmd):
        ret = subprocess.Popen(cmd, encoding=self.__encoding, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        # ret.wait()
        out, err = ret.communicate()
        # # FIXME 安装的时候 err的返回 会是 Success
        # if err:
        #     raise Exception(f"command failed,\nerr:{err}")
        return out, err

    def run_adb_cmd(self, cmd, mode=MultipleDevice):
        if mode == self.MultipleDevice:
            adb_cmd = f"adb -s {self.__serial} {cmd}"
        elif mode == self.SingleDevice:
            adb_cmd = f"adb {cmd}"
        else:
            raise Exception('should choose single or multiple device for adb cmd')
        return self.__run_cmd(adb_cmd)

    def run_shell_cmd(self, cmd, mode=MultipleDevice):
        if mode == self.MultipleDevice:
            adb_cmd = f"adb -s {self.__serial} shell {cmd}"
        elif mode == self.SingleDevice:
            adb_cmd = f"adb shell {cmd}"
        else:
            raise Exception('should choose single or multiple device for adb cmd')
        return self.__run_cmd(adb_cmd)

    def __tcp_forward(self, src, dst):
        adb_cmd = f"forward tcp:{src} tcp:{dst}"
        return self.run_adb_cmd(adb_cmd)

    def tcp_forward(self, src, dst):
        ret = self.__tcp_forward(src, dst)
        return ret

    def tcp_remove(self, src):
        adb_cmd = f"forward --remove tcp:{src}"
        ret = self.run_adb_cmd(adb_cmd)
        return ret

    def adjusted_device_pos(self, app_x, app_y):
        cur_screen = self.get_device_cur_screen()
        cur_width = cur_screen.width
        cur_height = cur_screen.height
        app_screen = self.get_device_app_screen()
        app_width = app_screen.width
        app_height = app_screen.height
        width_ratio = cur_width / app_width
        height_ratio = cur_height / app_height
        device_x = app_x * width_ratio
        device_y = app_y * height_ratio
        return device_x, device_y

    def __click_position(self, x, y):
        cmd = f"input tap {x} {y};echo $?"
        return self.run_shell_cmd(cmd)

    def click_position(self, x, y):
        # x, y = self.adjusted_device_pos(x, y)
        return self.__click_position(x, y)

    def __swipe_position(self, x1, y1, x2, y2, duration=250):
        cmd = f"input swipe {x1} {y1} {x2} {y2} {duration};echo $?"
        return self.run_shell_cmd(cmd)

    def swipe_position(self, x1, y1, x2, y2, duration=250):
        # x1, y1 = self.adjusted_device_pos(x1, y1)
        # x2, y2 = self.adjusted_device_pos(x2, y2)
        return self.__swipe_position(x1, y1, x2, y2, duration)

    def press_position(self, x, y, duration):
        return self.swipe_position(x, y, x, y, duration)

    def reboot(self):
        adb_cmd = f"reboot"
        return self.run_adb_cmd(adb_cmd)

    def get_cpu(self):
        adb_cmd = f'getprop ro.product.cpu.abi'
        return self.run_shell_cmd(adb_cmd)

    def start_app(self, package_name, package_main_activity_name):
        adb_cmd = f'am start {package_name}/{package_main_activity_name}'
        return self.run_shell_cmd(adb_cmd)

    def kill_app(self, package_name):
        adb_cmd = f'am force-stop {package_name}'
        return self.run_shell_cmd(adb_cmd)

    def __get_display_size(self):
        cmd = 'dumpsys window displays'
        return self.run_shell_cmd(cmd)

    def __get_device_display_info(self) -> tuple:
        # TODO 简化
        out = self.__get_display_size()
        lines = [l for l in out.split('\n')]
        search = [l for l in lines if 'init=' in l]
        search_dif = [s.split(' ') for s in search]
        curs_list = [[e[4:] for e in l if 'cur=' in e] for l in search_dif]
        apps_list = [[e[4:] for e in l if 'app=' in e] for l in search_dif]
        dif_index_list = sum(
            [[i for j, a in enumerate(apps) if curs_list[i][j] != a] for i, apps in enumerate(apps_list)],
            [])  # 找到不同的尺寸屏幕
        if len(dif_index_list) == 1:
            dif_index = dif_index_list[0]
            ret = search_dif[dif_index]
        elif len(dif_index_list) > 1:
            raise Exception('multi-display existed')
        else:
            ret = search_dif[0]
        ret = [i for i in ret if i != '']
        init = ret[0][5:].split('x')
        # init = ret[0][5:].split('x')
        # cur = [info[4:].split('x') for info in ret if 'cur=' in info]
        # flatten_cur = [item for sublist in cur for item in sublist]
        # app = [info[4:].split('x') for info in ret if 'app=' in info]
        # flatten_app = [item for sublist in app for item in sublist]
        #  # FIXME 用正则表达式
        cur = ret[2][4:].split('x')
        app = ret[3][4:].split('x')
        return Screen(init[0], init[1]), Screen(cur[0], cur[1]), Screen(app[0], app[1])

    def __get_device_init_screen(self) -> Screen:
        return self.__get_device_display_info()[0]

    def __get_device_cur_screen(self) -> Screen:
        return self.__get_device_display_info()[1]

    def __get_device_app_screen(self) -> Screen:
        return self.__get_device_display_info()[2]

    def get_device_cur_screen(self) -> Screen:
        return self.__get_device_cur_screen()

    def get_device_app_screen(self) -> Screen:
        return self.__get_device_app_screen()

    def __ps(self):
        adb_cmd = f'ps'
        return self.run_shell_cmd(adb_cmd)

    def __return_pid(self, package_name):
        adb_cmd = f'pidof {package_name}'
        return self.run_shell_cmd(adb_cmd)

    def return_pid(self, package_name) -> bool:
        # FIXME
        ps = self.__ps()
        # print("ps", ps)
        for line in ps:
            if package_name in line:
                return True
        return False
        # lines = ps.split('\n')
        # package = [line for line in lines if f'{package_name}' in line][0]
        # name = package.split(' ')
        # pid = name[4]
        # print(pid)
        # return int(pid)
        # ret = int(self.__return_pid(package_name))
        # return ret

    def check_app_running(self, package_name) -> bool:
        try:
            if self.return_pid(package_name):
                return True
            else:
                return False
        except:
            return False

    def __connected_tcp(self):
        adb_cmd = 'forward --list'
        return self.run_adb_cmd(adb_cmd)

    def connected_tcp(self):
        ret = self.__connected_tcp()
        if ret != '\n':
            ret = [l for l in ret.split('\n') if self.serial in l and self.__device_port in l]
            ret = [tab.split(' ') for tab in ret]
            local_ports = [i[1] for i in ret]
            return local_ports
        else:
            return []

    @property
    def tcp_connected(self) -> bool:
        local_ports = self.connected_tcp()
        if self.__local_port == None:
            raise Exception('to check tcp connection, you must first have a local port')
        for port in local_ports:
            if self.__local_port in port:
                return True
        return False

    def __get_current_focus(self):
        adb_cmd = 'dumpsys window'
        return self.run_shell_cmd(adb_cmd)

    def get_current_focus(self):
        out = self.__get_current_focus()
        out = [l for l in out.split('\n') if 'mCurrentFocus' in l]
        return out

    def check_app_focused(self, package_name) -> bool:
        current_focus = self.get_current_focus()
        for focus in current_focus:
            if package_name in focus:
                return True
        return False

    def check_adb_connection_ready(self, package_name):
        if self.connected != True:
            return False
            # raise Exception('device is not connected')
        if self.check_app_running(package_name) != True:
            return False
            # raise Exception('app is not running')
        if self.check_app_focused(package_name) != True:
            return False
            # raise Exception('app is not focused')
        if self.tcp_connected != True:
            return False
            # raise Exception('tcp is not connected')
        return True
