import json
import logging
import os
import socket
from logging.handlers import RotatingFileHandler

import alexis_src.protocol as protocol

"""
set up logging
"""
# fantom_logger = logging.getLogger()
# fantom_logger.setLevel(logging.DEBUG)
# formatter = logging.Formatter(
#     "%(asctime)s :: %(levelname)s :: %(message)s", "%H:%M:%S")
# # file
# if os.path.exists("./logs/fantom.log"):
#     os.remove("./logs/fantom.log")
# file_handler = RotatingFileHandler('./logs/fantom.log', 'a', 1000000, 1)
# file_handler.setLevel(logging.DEBUG)
# file_handler.setFormatter(formatter)
# fantom_logger.addHandler(file_handler)
# # stream
# stream_handler = logging.StreamHandler()
# stream_handler.setLevel(logging.WARNING)
# fantom_logger.addHandler(stream_handler)


class ClientPlayer:
    def __init__(self, host, port, ai):
        self.socket_host = host
        self.socket_port = port
        self.ai = ai
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def connect(self):
        self.socket.connect((self.socket_host, self.socket_port))

    def reset(self):
        self.socket.close()

    def handle_json(self, data):
        data = json.loads(data)
        response = self.answer(data)
        bytes_data = json.dumps(response).encode("utf-8")
        protocol.send_json(self.socket, bytes_data)

    def run(self):
        self.connect()

        while True:
            received_message = protocol.receive_json(self.socket)
            if received_message:
                data = json.loads(received_message)
                response = self.ai.get_next_play(data)
                bytes_data = json.dumps(response).encode("utf-8")
                protocol.send_json(self.socket, bytes_data)
            else:
                print("no message, finished learning")
                break
