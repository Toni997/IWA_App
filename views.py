import socket
from http.cookies import SimpleCookie
import re
import datetime

import hashing
from template_engine import TemplateEngine
import db_collections
import db_users
import db_sessions

CRLF = b'\r\n'


def login_required(func):
    def wrapper(client, cookies: SimpleCookie = None, multipart_data: dict = None):
        if cookies:
            session_hash = cookies.get('sessId')
            if not session_hash:
                return redirect_to(client, b'/login')
            session_hash = session_hash.coded_value
            user = db_sessions.get_session_with_user(session_hash)
            if not user or user['valid_until'] < datetime.datetime.now():
                return redirect_to(client, b'/login', cookies)
            return func(client, cookies, multipart_data)
        return redirect_to(client, b'/login', cookies)
    return wrapper


def redirect_if_logged_in(func):
    def wrapper(client, cookies: SimpleCookie = None, multipart_data: dict = None):
        if cookies:
            session_hash = cookies.get('sessId')
            if not session_hash:
                return func(client, cookies, multipart_data)
            session_hash = session_hash.coded_value
            user = db_sessions.get_session_with_user(session_hash)
            if not user or user['valid_until'] < datetime.datetime.now():
                return func(client, cookies, multipart_data)
            return redirect_to(client, b'/', cookies)
        return func(client, cookies, multipart_data)
    return wrapper


def send_file(client: socket, file_name: str, content_type: bytes,
              cookies: SimpleCookie = None, context: dict = None) -> None:
    msg = b'HTTP/1.1 200 OK' + CRLF
    msg += b'Content-Type: ' + content_type + CRLF
    if cookies:
        msg += cookies.output().encode() + CRLF
    msg += CRLF
    msg += bytes(TemplateEngine(file_name, context))
    client.send(msg)


def redirect_to(client: socket, location: bytes, cookies: SimpleCookie = None) -> None:
    msg = b"HTTP/1.1 302 Found" + CRLF
    msg += b"Content-Type: text/html" + CRLF
    if cookies:
        msg += cookies.output().encode() + CRLF
    msg += b"Location: " + location + CRLF
    msg += CRLF
    msg += b"<h1>Redirecting...</h1>"
    client.send(msg)


def bad_request(client: socket, location: bytes) -> None:
    msg = b"HTTP/1.1 400 Bad Request" + CRLF
    msg += b"Content-Type: text/html" + CRLF
    msg += b"Location: " + location + CRLF
    msg += CRLF
    msg += b"<h1>Error: Bad Request</h1>"
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


@login_required
def get_home_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    context = dict()
    context['collections'] = db_collections.get_all()
    context['page_title'] = 'Home'
    send_file(client, 'pages/index.html', b'text/html', cookies, context)


@redirect_if_logged_in
def get_signup_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    # TODO check if already authenticated
    context = dict()
    context['page_title'] = 'Sign Up'
    send_file(client, 'pages/signup.html', b'text/html', cookies, context)


@redirect_if_logged_in
def get_login_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    # TODO check if already authenticated
    context = dict()
    context['page_title'] = 'Log In'
    send_file(client, 'pages/login.html', b'text/html', cookies, context)


@redirect_if_logged_in
def post_login_page(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None) -> None:
    username = multipart_data['username'][0]
    user = db_users.get_one_with_username(username)
    if not user:
        return redirect_to(client, b'/login')

    salt = bytes.fromhex(user[0]['salt'])
    pw_hash = bytes.fromhex(user[0]['password_hash'])
    password = multipart_data['password'][0]
    if not hashing.is_correct_password(salt, pw_hash, password):
        return redirect_to(client, b'/login')

    user_id = user[0]['user_id']
    valid_until = str(datetime.datetime.now() + datetime.timedelta(days=7))
    session_hash = hashing.session_token()
    cookies = SimpleCookie(f"sessId={session_hash}; HttpOnly")
    db_sessions.insert_one(session_hash, user_id, valid_until)
    redirect_to(client, b'/', cookies)


def post_signup_page(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None) -> None:
    email = multipart_data['email'][0]
    if not re.match(db_users.EMAIL_PATTERN, email):
        return redirect_to(client, b'/signup')

    username = multipart_data['username'][0]
    if not re.match(db_users.USERNAME_PATTERN, username):
        return redirect_to(client, b'/signup')

    user_exists = db_users.get_one_with_email_or_username(email, username)
    if user_exists:
        return redirect_to(client, b'/signup')

    password = multipart_data['password'][0]
    repeat_password = multipart_data['repeat-password'][0]
    if len(password) >= 8 and password != repeat_password:
        return redirect_to(client, b'/signup')

    salt, pw_hash = hashing.hash_new_password(password)
    db_users.insert_one(email, username, salt, pw_hash)

    redirect_to(client, b'/login')


@login_required
def post_image(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None) -> None:
    # TODO process post request
    redirect_to(client, b'/', cookies)


@login_required
def post_collection(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None) -> None:
    name = multipart_data['name']
    if name:
        name = name[0]
        if name.strip():
            db_collections.insert_one(name)

    redirect_to(client, b'/', cookies)
