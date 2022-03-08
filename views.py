import socket
from http.cookies import SimpleCookie

import sqlCollections
from TemplateEngine import TemplateEngine

CRLF = b'\r\n'


def send_file(client: socket, file_name: str, content_type: bytes, cookies: SimpleCookie = None) -> None:
    list_of_collections = [
        {
            b'collection_id': b'1',
            b'name': b'Cars'
        },
        {
            b'collection_id': b'2',
            b'name': b'Tech'
        },
        {
            b'collection_id': b'3',
            b'name': b'Animals'
        },
    ]
    msg = b'HTTP/1.1 200 OK' + CRLF
    msg += b'Content-Type: ' + content_type + CRLF
    if cookies:
        msg += cookies + CRLF
    msg += CRLF
    msg += bytes(TemplateEngine(file_name, {'collections': list_of_collections}))
    client.send(msg)


def get_favicon(client: socket) -> None:
    send_file(client, 'favicon.ico', b'image/x-icon')


def get_style(client: socket) -> None:
    send_file(client, 'style.css', b'text/css')


def get_javascript(client: socket) -> None:
    send_file(client, 'script.js', b'text/javascript')


def get_error_page(client: socket) -> None:
    send_file(client, '404.html', b'text/html')


def get_error_image(client: socket) -> None:
    send_file(client, '404.png', b'text/jpeg')


def get_home_page(client: socket, cookies: SimpleCookie) -> None:
    send_file(client, 'main.html', b'text/html', cookies)


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
        sqlCollections.insert_one(name)

    msg = b"HTTP/1.1 302 Found" + CRLF
    msg += b"Content-Type: text/html" + CRLF
    msg += b"Location: /" + CRLF
    msg += CRLF
    msg += b"<h1>Redirecting...</h1>"
    client.send(msg)
