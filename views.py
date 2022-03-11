import socket
from http.cookies import SimpleCookie
import re

import hashing
from template_engine import TemplateEngine
import db_collections
import db_users

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


def redirect_to(client: socket, location: bytes) -> None:
    msg = b"HTTP/1.1 302 Found" + CRLF
    msg += b"Content-Type: text/html" + CRLF
    msg += b"Location: " + location + CRLF
    msg += CRLF
    msg += b"<h1>Redirecting...</h1>"
    client.send(msg)


def get_favicon(client: socket) -> None:
    send_file(client, 'static/favicon.ico', b'image/x-icon')


def get_style(client: socket) -> None:
    send_file(client, 'static/style.css', b'text/css')


def get_javascript(client: socket) -> None:
    send_file(client, 'static/script.js', b'text/javascript')


def get_error_page(client: socket) -> None:
    context = dict()
    context['page_title'] = 'Error 404'
    send_file(client, 'pages/404.html', b'text/html', cookies=None, context=context)


def get_error_image(client: socket) -> None:
    send_file(client, 'static/404.png', b'text/jpeg')


def get_home_page(client: socket, cookies: SimpleCookie) -> None:
    context = dict()
    context['collections'] = db_collections.get_all()
    context['page_title'] = 'Home'
    send_file(client, 'pages/index.html', b'text/html', cookies, context)


def get_signup_page(client: socket, cookies: SimpleCookie) -> None:
    # TODO check if already authenticated
    context = dict()
    context['page_title'] = 'Sign Up'
    send_file(client, 'pages/signup.html', b'text/html', cookies, context)


def get_login_page(client: socket, cookies: SimpleCookie) -> None:
    # TODO check if already authenticated
    context = dict()
    context['page_title'] = 'Log In'
    send_file(client, 'pages/login.html', b'text/html', cookies, context)


def post_login_page(client: socket, multipart_data) -> None:
    username = multipart_data['username'][0]


def post_signup_page(client: socket, multipart_data) -> None:
    email = multipart_data['email'][0]
    if not re.match(db_users.EMAIL_PATTERN, email):
        redirect_to(client, b'/signup')
        return

    username = multipart_data['username'][0]
    if not re.match(db_users.USERNAME_PATTERN, username):
        redirect_to(client, b'/signup')
        return

    user_exists = db_users.get_one_with_email_or_username(email, username)
    if user_exists:
        redirect_to(client, b'/signup')
        return

    password = multipart_data['password'][0]
    repeat_password = multipart_data['repeat-password'][0]
    if len(password) >= 8 and password != repeat_password:
        redirect_to(client, b'/signup')
        return

    salt, pw_hash = hashing.hash_new_password(password)
    db_users.insert_one(email, username, salt, pw_hash)

    redirect_to(client, b'/login')


def post_image(client: socket) -> None:
    # TODO process post request
    redirect_to(client, b'/')


def post_collection(client: socket, name: str) -> None:
    if name.strip():
        db_collections.insert_one(name)

    redirect_to(client, b'/')
