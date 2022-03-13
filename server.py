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
    if not req.get_path():
        print(req.get_header())
    method = req.get_method()
    paths = req.get_path().split(b'/')

    match paths[1]:
        case b'favicon.ico':
            views.get_favicon(c)
        case b'style.css':
            views.get_style(c)
        case b'script.js':
            views.get_javascript(c)
        case b'':
            views.get_home_page(c, req.get_cookies())
        case b'images':
            if len(paths) <= 2:
                match method:
                    case b'GET':
                        views.get_images_page(c, req.get_cookies())
                    case b'POST':
                        views.post_images_page(c, req.get_cookies(), req.get_multipart_data())
            elif 3 <= len(paths) <= 4:
                if paths[2].isdigit():
                    if len(paths) == 3:
                        match method:
                            case b'GET':
                                views.get_image(c, req.get_cookies(), req.get_multipart_data(), int(paths[2]))
                            case b'POST':
                                views.delete_image(c, req.get_cookies(), req.get_multipart_data(), int(paths[2]))
                    else:
                        views.get_image_details(c, req.get_cookies(), req.get_multipart_data(), int(paths[2]))
                else:
                    views.get_error_page(c)

        case b'images-json':
            views.get_images_json(c, req.get_cookies())
        case b'settings':
            views.get_settings_page(c, req.get_cookies())
        case b'change-password':
            views.post_settings_page(c, req.get_cookies(), req.get_multipart_data())
        case b'login':
            match method:
                case b'GET':
                    views.get_login_page(c, req.get_cookies())
                case b'POST':
                    views.post_login_page(c, req.get_cookies(), req.get_multipart_data())
        case b'signup':
            match method:
                case b'GET':
                    views.get_signup_page(c, req.get_cookies())
                case b'POST':
                    views.post_signup_page(c, req.get_cookies(), req.get_multipart_data())
        case b'image/add':
            views.post_image(c,  req.get_cookies(), req.get_multipart_data())
        case b'collections':
            views.post_collection(c, req.get_cookies(), req.get_multipart_data())
        case b'logout':
            views.post_logout(c, req.get_cookies(), req.get_multipart_data())
        case b'404.png':
            views.get_error_image(c)
        case _:
            views.get_error_page(c)


while True:
    client, address = server.accept()
    print(f'Connected to client: {address}')

    handle_request(client)

    client.close()


