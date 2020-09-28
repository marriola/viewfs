import logging
import os
import os.path
import pickle
import socket
from stat import S_IRWXU
import sys
import time

class Transport:
    def __init__(self, config):
        if 'AF_UNIX' in dir(socket):
            self.unix = True
            self.socket = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            self.socket_path = config.view.socket_path
        else:
            self.unix = False
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket_path = ('localhost', config.view.socket_port)

    def connect(self):
        raise NotImplementedError()
    
    def send(self, message):
        message_bytes = pickle.dumps(message)
        length = len(message_bytes).to_bytes(8, byteorder='big')
        self.conn.send(length)
        self.conn.send(message_bytes)

    def receive(self):
        length = int.from_bytes(self.conn.recv(8), byteorder='big')
        message_bytes = self.conn.recv(length)
        return pickle.loads(message_bytes)

    def close(self):
        raise NotImplementedError()

    def __del__(self):
        if self.socket:
            self.close()

class Server(Transport):
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger('transport.Server')

        self.socket.bind(self.socket_path)
        
        if self.unix:
            os.chmod(self.socket_path, S_IRWXU)

        self.socket.listen(1)

    def connect(self):
        self.logger.debug('waiting for connection from client')
        self.conn, _ = self.socket.accept()
        self.logger.debug('accepted connection from client')

    def close(self):
        if self.conn:
            self.conn.close()

        self.socket.close()
        self.socket = None

        if self.unix:
            os.remove(self.socket_path)

class Client(Transport):
    def __init__(self, config):
        super().__init__(config)
        self.logger = logging.getLogger('transport.Client')
        self.conn = self.socket

    def connect(self):
        self.logger.debug('connecting to server')
        
        while True:
            try:
                self.socket.connect(self.socket_path)
                break
            except:
                time.sleep(1)

        self.logger.debug('connected to %s' % str(self.socket_path))

    def close(self):
        self.socket.close()
        self.socket = None
