'''
File:adb_connection.py
Author:ezgameworkplace
Date:2022/11/25
'''
import subprocess

class ADBConnection():

    SingleDevice = 0
    MultipleDevice = 1

    __slots__ = ['__serial', '__encoding', '__connected', '__local_port', '__device_port']

    def __init__(self, serial, encoding='utf-8', device_port='27019'):
        self.__serial = serial
        self.__encoding = encoding
        self.__connected = False
        self.__local_port = None
        self.__device_port = device_port

    def __str__(self):
        return f'adb connection info:\nserial:{self.__serial}'

    @property
    def serial(self):
        return self.__serial

    @property
    def device_port(self):
        return self.__device_port

    @property
    def connected(self):
        if self.serial in self.connected_devices():
            self.__connected = True
        else:
            self.__connected = False
        return self.__connected

    def __run_cmd(self, cmd):
        ret = subprocess.Popen(cmd, encoding=self.__encoding, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret.wait()
        out, err = ret.communicate()
        if err:
            raise Exception(f"adb command failed,\nerr:{err}")
        return out

    def run_cmd(self, cmd, mode=MultipleDevice):
        if mode == self.MultipleDevice:
            adb_cmd = f"adb -s {self.__serial} {cmd}"
        elif mode == self.SingleDevice:
            adb_cmd = f"adb {cmd}"
        else:
            raise Exception('should choose single or multiple device for adb cmd')
        ret = subprocess.Popen(adb_cmd, encoding=self.__encoding, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret.wait()
        out, err = ret.communicate()
        if err:
            raise Exception(f"adb command failed,\nerr:{err}")
        return out

    def run_os_cmd(self, cmd):
        # FIXME using shell=True is not good
        ret = subprocess.Popen(cmd, encoding=self.__encoding, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        ret.wait()
        out, err = ret.communicate()
        if err:
            raise Exception(f"command failed,\nerr:{err}")
        return out

    def __connected_devices(self):
        adb_cmd = f'devices'
        return self.run_cmd(adb_cmd)

    def connected_devices(self):
        devices_header = 'List of devices attached'
        devices_connected = 'device'
        ret = self.__connected_devices()
        lines = [line for line in ret.split('\n') if line != '' and line != devices_header]
        tabs = [line.split('\t') for line in lines]
        devices_serial = [tab[0] for tab in tabs if tab[1] == devices_connected]
        return devices_serial

    def __exist_local_port(self):
        os_cmd = f"netstat -nao | findstr {self.__local_port}"
        return self.run_os_cmd(os_cmd)

    def exist_local_port(self)->bool:
        # TODO need more info
        ret = self.__exist_local_port()
        if ret != '':
            return True
        else:
            return False

    def __exist_device_port(self):
        adb_cmd = f"shell netstat -a | grep {self.__device_port}"
        return self.run_cmd(adb_cmd)

    def exist_device_port(self)->bool:
        if self.connected == True:
            ret = self.__exist_device_port()
            if ret != '':
                return True
            else:
                return False
        else:
            return False

    def __tcp_forward(self, src, dst):
        adb_cmd = f"forward tcp:{src} tcp:{dst}"
        return self.run_cmd(adb_cmd)

    def tcp_forward(self, src, dst):
        self.__local_port = src
        self.__device_port = dst
        ret = self.__tcp_forward(src, dst)
        return ret

    def tcp_remove(self, src):
        adb_cmd = f"forward --remove tcp:{src}"
        ret = self.run_cmd(adb_cmd)
        return ret

    def click_position(self, x, y):
        cmd = f"shell input tap {x} {y};echo $?"
        return self.run_cmd(cmd)

    def swipe_position(self, x1, y1, x2, y2, duration=250):
        cmd = f"shell input swipe {x1} {y1} {x2} {y2} {duration};echo $?"
        return self.run_cmd(cmd)

    def press_position(self, x, y, duration):
        return self.swipe_position(x, y, x, y, duration)

    def reboot(self):
        adb_cmd = f"reboot"
        return self.run_cmd(adb_cmd)

    def get_cpu(self):
        adb_cmd = f'shell getprop ro.product.cpu.abi'
        return self.run_cmd(adb_cmd)

    def start_app(self, package_name, package_main_activity_name):
        adb_cmd = f'shell am start {package_name}/{package_main_activity_name}'
        return self.run_cmd(adb_cmd)

    def kill_app(self, package_name):
        adb_cmd = f'shell am force-stop {package_name}'
        return self.run_cmd(adb_cmd)

    def __return_pid(self, package_name):
        adb_cmd = f'shell pidof {package_name}'
        return self.run_cmd(adb_cmd)

    def return_pid(self, package_name)->int:
        return int(self.__return_pid(package_name))

    def check_app_running(self, package_name)->bool:
        try:
            self.return_pid(package_name)
            return True
        except:
            return False


