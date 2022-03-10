import socket
import threading
import os

from http_request import HttpRequest
import views

HOST = '127.0.0.1'
PORT = 8090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen(5)

CRLF = b"\r\n"


def handle_request(c: socket):
    req = HttpRequest(c)

    match req.get_path():
        case b'/favicon.ico':
            views.get_favicon(c)
        case b'/style.css':
            views.get_style(c)
        case b'/script.js':
            views.get_javascript(c)
        case b'/':
            views.get_home_page(c, req.get_cookies())
        case b'/signup':
            views.get_signup_page(c, req.get_cookies())
        case b'/image/add':
            views.post_image(c)
        case b'/collection/add':
            multipart_data = req.get_multipart_data()
            name = multipart_data.get('collection-name')[0]
            views.post_collection(c, name)
        case b'/404.png':
            views.get_error_image(c)
        case _:
            views.get_error_page(c)


while True:
    client, address = server.accept()
    print(f'Connected to client: {address}')

    handle_request(client)

    client.close()


