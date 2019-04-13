# -*- coding: utf-8 -*-
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import socket
import time


def main():
    s = socket.socket()

    # Define the port on which you want to connect
    port = 1234

    # connect to the server on local computer
    s.connect(('127.0.0.1', port))
    print(s.getsockname())
    # receive data from the server
    while True:
        s.sendall(b'hello')
        data = s.recv(1024)
        print(data)


    s.close()


if __name__ == "__main__":
    main()
