'''
File:device.py
Author:ezgameworkplace
Date:2022/12/7
'''
class Device(object):

    phone = 'phone'
    nox_vb = 'nox virtual box'

    def __init__(self, serial=None, type=None):
        self.__serial = serial
        self.__type = type

    @property
    def serial(self):
        return self.__serial

    @property
    def type(self):
        return self.__type


    def __str__(self):
        return f'device serial:{self.serial}\tdevice type:{self.__type}'

class Phone(Device):

    def __init__(self):
        super().__init__(self.serial, self.phone)

class Nox_VB(Device):

    def __init__(self):
        super().__init__(self.serial, self.nox_vb)
