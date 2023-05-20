'''
File:client_socket.py
Author:ezgameworkplace
Date:2022/11/25
'''
import json
import socket
import struct


class ClientSocket:
    __slots__ = ['__ip', '__port', '__encoding', '__timeout', '_client_socket', '__connected']

    def __init__(self, ip: str, port: int, encoding: str = 'utf-8', timeout: int = 2):
        self.__ip = ip
        self.__port = port
        self.__encoding = encoding
        self.__timeout = timeout
        self._client_socket = None
        self.__connected = False

    def __str__(self):
        return f'socket info:\nip:{self.__ip}\nport:{self.__port}\nclient socket:{self._client_socket}'

    @property
    def encoding(self):
        return self.__encoding

    @property
    def ip(self):
        return self.__ip

    @property
    def port(self):
        return self.__port

    @property
    def timeout(self):
        return self.__timeout

    @property
    def client_socket(self):
        return self._client_socket

    @client_socket.setter
    def client_socket(self, value):
        self._client_socket = value

    def __ping(self):
        return self.send_command(100,
                                 None)  # ret = {'cmd': 100, 'status': 0, 'data': {'sdkVersion': '2.0.0', 'engine': 'Unity3D', 'engineVersion': '2018.4.11f1', 'sdkUIType': 'NGUI'}}

    def ping(self) -> bool:
        try:
            self.__ping()
            return True
        except:
            return False

    @property
    def connected(self) -> bool:
        if self._client_socket:
            if self.ping() == True:
                self.__connected = True
            else:
                self.__connected = False
        else:
            self.__connected = False
        return self.__connected

    def __create_socket(self):
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        self._client_socket.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        self._client_socket.settimeout(self.__timeout)
        self._client_socket.setblocking(True)
        return self._client_socket

    def __connect(self):
        self._client_socket = self.__create_socket()
        self._client_socket.connect((self.__ip, int(self.__port)))

    def connect(self):
        self.__connect()
        return self._client_socket

    def disconnect(self):
        try:
            self._client_socket.close()
        except Exception as e:
            raise Exception(f'disconnection failed, \nerr:{e}')

    def reconnect_socket(self):
        try:
            self.disconnect()
            new_socket = self.connect()
        except:
            new_socket = self.connect()
        return new_socket

    def _send_data(self, data):
        if self._client_socket:
            try:
                serialized = json.dumps(data)
                length = len(serialized)
                buff = struct.pack("i", length)
                self._client_socket.send(buff)
                self._client_socket.sendall(bytes(serialized, encoding=self.__encoding))
            except Exception as e:
                raise Exception(f'send failed, \nerr:{e}')
        else:
            self.connect()
            self._send_data(data)

    def __recv_package(self) -> dict:
        length_buffer = self._client_socket.recv(4)
        if length_buffer:
            total = struct.unpack_from("i", length_buffer)[0]
        else:
            raise Exception('recv failed')
        view = memoryview(bytearray(total))
        next_offset = 0
        while total - next_offset > 0:
            recv_size = self._client_socket.recv_into(view[next_offset:], total - next_offset)
            next_offset += recv_size
        deserialized = json.loads(str(view.tobytes(), encoding=self.__encoding))
        return deserialized

    def _recv_data(self) -> dict:
        deserialized = self.__recv_package()
        if deserialized['status'] != 0:
            message = "Error code: " + str(deserialized['status']) + " msg: " + deserialized['data']
            raise Exception(message)
        return deserialized

    def send_command(self, cmd: int, params: dict or None = None) -> dict:
        if not params:
            params = ""
        command = {}
        command["cmd"] = cmd
        command["value"] = params
        self._send_data(command)
        ret = self._recv_data()
        return ret
