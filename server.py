import socket
import threading
import os
from http.cookies import SimpleCookie

from http_request import HttpRequest
import views
from request_handler import handle_request

HOST = '127.0.0.1'
PORT = 8090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen(5)

CRLF = b"\r\n"

while True:
    client, address = server.accept()
    print(f'Connected to client: {address}')

    handle_request(client)

    client.close()


