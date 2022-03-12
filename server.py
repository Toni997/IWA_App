import socket
import threading
import os
from http.cookies import SimpleCookie

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
    method = req.get_method()

    match req.get_path():
        case b'/favicon.ico':
            views.get_favicon(c)
        case b'/style.css':
            views.get_style(c)
        case b'/script.js':
            views.get_javascript(c)
        case b'/':
            views.get_home_page(c, req.get_cookies())
        case b'/login':
            match method:
                case b'GET':
                    views.get_login_page(c, req.get_cookies())
                case b'POST':
                    views.post_login_page(c, req.get_cookies(), req.get_multipart_data())
        case b'/signup':
            match method:
                case b'GET':
                    views.get_signup_page(c, req.get_cookies())
                case b'POST':
                    views.post_signup_page(c, req.get_cookies(), req.get_multipart_data())
        case b'/image/add':
            views.post_image(c,  req.get_multipart_data())
        case b'/collection/add':
            views.post_collection(c, req.get_multipart_data())
        case b'/404.png':
            views.get_error_image(c)
        case _:
            views.get_error_page(c)


while True:
    client, address = server.accept()
    print(f'Connected to client: {address}')

    handle_request(client)

    client.close()


