'''
File:nox_console.py
Author:ezgameworkplace
Date:2022/11/24
'''
import subprocess

# 参考 https://support.yeshen.com/zh-CN/qt/adb

class NoxConsole():

    __slots__ = ['_console_path', '_encoding']

    def __init__(self, console_path, encoding='ANSI'):
        self._console_path = console_path
        self._encoding = encoding

    def __str__(self):
        return f'nox_console at path:{self.console_path}'

    @property
    def console_path(self):
        return self._console_path

    def _send_cmd(self, cmd):
        ret = subprocess.Popen(cmd, encoding=self._encoding, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ret.wait()
        out, err = ret.communicate()
        if err:
            raise Exception(f"nox console command failed,\nerr:{err}")
        return out

    def launch(self, name):
        cmd = fr"{self.console_path} launch -name:{name}"
        return self._send_cmd(cmd)

    def quit(self, name):
        cmd = fr"{self.console_path} quit -name:{name}"
        return self._send_cmd(cmd)

    def quit_all(self):
        cmd = fr"{self.console_path} quitall"
        return self._send_cmd(cmd)

    def add_vb(self, name, system_type=7):
        cmd = fr"{self.console_path} add -name:{name} -systemtype:{system_type}"
        return self._send_cmd(cmd)

    def copy_vb(self, dst, src):
        cmd = fr"{self.console_path} copy -name:{dst} -from:{src}"
        return self._send_cmd(cmd)

    def remove_vb(self, name, index=None):
        if index:
            cmd = fr"{self.console_path} remove -name:{name} -index:{index}"
        else:
            cmd = fr"{self.console_path} remove -name:{name}"
        return self._send_cmd(cmd)

    def install_app(self, name, src, index=None):
        if index:
            cmd = fr"{self.console_path} installapp -name:{name} -index:{index} -filename:{src}"
        else:
            cmd = fr"{self.console_path} installapp -name:{name} -filename:{src}"
        return self._send_cmd(cmd)

    def uninstall_app(self, name, packagename, index=None):
        if index:
            cmd = fr"{self.console_path} uninstallapp -name:{name} -index:{index} -packagename:{packagename}"
        else:
            cmd = fr"{self.console_path} uninstallapp -name:{name} -packagename:{packagename}"
        return self._send_cmd(cmd)

    def run_app(self, name, packagename, index=None):
        if index:
            cmd = fr"{self.console_path} runapp -name:{name} -index:{index} -packagename:{packagename}"
        else:
            cmd = fr"{self.console_path} runapp -name:{name} -packagename:{packagename}"
        return self._send_cmd(cmd)

    def kill_app(self, name, packagename, index=None):
        if index:
            cmd = fr"{self.console_path} killapp -name:{name} -index:{index} -packagename:{packagename}"
        else:
            cmd = fr"{self.console_path} killapp -name:{name} -packagename:{packagename}"
        return self._send_cmd(cmd)

    def kill_all_app(self, name, index=None):
        if index:
            cmd = fr"{self.console_path} killappall -name:{name} -index:{index}"
        else:
            cmd = fr"{self.console_path} killappall -name:{name}"
        return self._send_cmd(cmd)

    def relocate(self, name, lng, lat, index=None):
        if index:
            cmd = fr"{self.console_path} locate -name:{name} -index:{index} -gps:{lng},{lat}"
        else:
            cmd = fr"{self.console_path} locate -name:{name} -gps:{lng},{lat}"
        return self._send_cmd(cmd)

    @property
    def list_vb(self):
        cmd = fr"{self.console_path} list"
        return self._send_cmd(cmd)

    @property
    def running_vb(self)->list:
        vb_names = self.vb_names
        vb_pids = self.vb_pids
        return [v for i, v in enumerate(vb_names) if vb_pids[i] != '-1']

    @property
    def vb_indices(self):
        out = self.list_vb
        return [i.split(',')[0] for i in out.split('\n') if i!='']

    @property
    def vb_init_names(self):
        out = self.list_vb
        return [i.split(',')[1] for i in out.split('\n') if i!='']

    @property
    def vb_names(self):
        out = self.list_vb
        return [i.split(',')[2] for i in out.split('\n') if i!='']

    @property
    def vb_top_windows(self):
        out = self.list_vb
        return [i.split(',')[3] for i in out.split('\n') if i!='']

    @property
    def vb_toolbar_windows(self):
        out= self.list_vb
        return [i.split(',')[4] for i in out.split('\n') if i!='']

    @property
    def vb_bound_windows(self):
        out = self.list_vb
        return [i.split(',')[5] for i in out.split('\n') if i!='']

    @property
    def vb_pids(self):
        out = self.list_vb
        return [i.split(',')[6] for i in out.split('\n') if i!='']

    def reboot(self, name, index=None):
        if index:
            cmd = fr"{self.console_path} reboot -name:{name} -index:{index}"
        else:
            cmd = fr"{self.console_path} reboot -name:{name}"
        return self._send_cmd(cmd)

    def rename(self, old, new, index=None):
        if index:
            cmd = fr"{self.console_path} rename -name:{old} -index:{index} -title:{new}"
        else:
            cmd = fr"{self.console_path} rename -name:{old} -title:{new}"
        return self._send_cmd(cmd)

