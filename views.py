import socket
from http.cookies import SimpleCookie

import db_collections
from template_engine import TemplateEngine

CRLF = b'\r\n'


def send_file(client: socket, file_name: str, content_type: bytes,
              cookies: SimpleCookie = None, context: dict = None) -> None:
    msg = b'HTTP/1.1 200 OK' + CRLF
    msg += b'Content-Type: ' + content_type + CRLF
    if cookies:
        msg += bytes(cookies) + CRLF
    msg += CRLF
    msg += bytes(TemplateEngine(file_name, context))
    client.send(msg)


def get_favicon(client: socket) -> None:
    send_file(client, 'static/favicon.ico', b'image/x-icon')


def get_style(client: socket) -> None:
    send_file(client, 'static/style.css', b'text/css')


def get_javascript(client: socket) -> None:
    send_file(client, 'static/script.js', b'text/javascript')


def get_error_page(client: socket) -> None:
    send_file(client, 'pages/404.html', b'text/html')


def get_error_image(client: socket) -> None:
    send_file(client, 'static/404.png', b'text/jpeg')


def get_home_page(client: socket, cookies: SimpleCookie) -> None:
    context = dict()
    context['collections'] = db_collections.get_all()
    send_file(client, 'pages/index.html', b'text/html', cookies, context)


def get_signup_page(client: socket, cookies: SimpleCookie) -> None:
    send_file(client, 'pages/signup.html', b'text/html', cookies)


def post_image(client: socket) -> None:
    # TODO process post request
    msg = b"HTTP/1.1 200 OK" + CRLF
    msg += b"Content-Type: text/html" + CRLF
    msg += b"Location: /" + CRLF
    msg += CRLF
    msg += b"<h1>Redirecting...</h1>"
    client.send(msg)


def post_collection(client: socket, name: str) -> None:
    if name.strip():
        db_collections.insert_one(name)

    msg = b"HTTP/1.1 302 Found" + CRLF
    msg += b"Content-Type: text/html" + CRLF
    msg += b"Location: /" + CRLF
    msg += CRLF
    msg += b"<h1>Redirecting...</h1>"
    client.send(msg)
