import os
import socket
from http.cookies import SimpleCookie
import re
import datetime
import imghdr
from io import BytesIO
import json

import db_images
import hashing
from template_engine import TemplateEngine
import db_collections
import db_users
import db_sessions

CRLF = b'\r\n'


def default_converter(o):
    if isinstance(o, datetime.datetime):
        return o.__str__()


def account_required(admin_required: bool = False):
    def login_required(func):
        def wrapper(client, cookies: SimpleCookie = None, multipart_data: dict = None, *args):
            if cookies:
                session_hash = cookies.get('sessId')
                if not session_hash:
                    return redirect_to(client, b'/login')
                session_hash = session_hash.coded_value
                user = db_sessions.get_session_with_user(session_hash)
                if not user or user['valid_until'] < datetime.datetime.now():
                    return redirect_to(client, b'/login', cookies)
                if admin_required:
                    is_admin = user['is_admin']
                    if not is_admin:
                        return redirect_to(client, b'/login', cookies)
                return func(client, cookies, multipart_data, *args)
            return redirect_to(client, b'/login', cookies)
        return wrapper
    return login_required


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
        if cookies.get('sessId'):
            cookies['sessId']['path'] = '/'
            cookies['sessId']['httponly'] = 'HttpOnly'
        msg += cookies.output().encode() + CRLF
    msg += CRLF
    msg += bytes(TemplateEngine(file_name, context))
    client.send(msg)


def send_json(client: socket, dict_to_send: dict = None) -> None:
    json_to_send = json.dumps(dict_to_send, default=default_converter).encode()
    msg = b'HTTP/1.1 200 OK' + CRLF
    msg += b'Content-Type: ' + b'text/json' + CRLF
    msg += CRLF
    msg += json_to_send
    client.send(msg)


def send_image(client: socket, file_name: str) -> None:
    msg = b'HTTP/1.1 200 OK' + CRLF
    msg += b'Content-Type: ' + b'image/jpeg, image/png' + CRLF
    msg += CRLF
    with open(file_name, 'rb') as file:
        msg += file.read()
    client.send(msg)


def redirect_to(client: socket, location: bytes, cookies: SimpleCookie = None) -> None:
    msg = b"HTTP/1.1 302 Found" + CRLF
    msg += b"Content-Type: text/html" + CRLF
    if cookies:
        if cookies.get('sessId'):
            cookies['sessId']['path'] = '/'
            cookies['sessId']['httponly'] = 'HttpOnly'
        msg += cookies.output().encode() + CRLF
    msg += b"Location: " + location + CRLF
    msg += CRLF
    msg += b"<h1>Redirecting...</h1>"
    client.send(msg)


def bad_request(client: socket) -> None:
    msg = b"HTTP/1.1 400 Bad Request" + CRLF
    msg += b"Content-Type: text/html" + CRLF
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


@account_required()
def get_home_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    context = dict()
    context['collections'] = db_collections.get_all()
    context['page_title'] = 'Home'
    send_file(client, 'pages/index.html', b'text/html', cookies, context)


@account_required(admin_required=True)
def get_images_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    context = dict()
    context['images'] = db_images.get_all()
    context['page_title'] = 'Images'
    send_file(client, 'pages/images-table.html', b'text/html', cookies, context)


@account_required()
def get_images_json(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    collections = db_collections.get_all()
    dict_to_send = dict()
    for collection in collections:
        dict_to_send[collection['name']] = db_images.get_all_with_collection_id(collection['collection_id'])
    send_json(client, dict_to_send)


@account_required()
def get_image(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None, image_id: int = None):
    image = db_images.get_one(image_id)
    if not image:
        return redirect_to(client, b'/')
    path = image['path']
    send_image(client, path)


@account_required()
def get_image_details(client: socket, cookies: SimpleCookie = None,
                      multipart_data: dict = None, image_id: int = None) -> None:
    now = datetime.datetime.now()
    now_str = now.__str__()
    viewed_cookies = cookies.get('viewed')
    if not viewed_cookies:
        viewed = {
            str(image_id): now_str
        }
    else:
        viewed = json.loads(viewed_cookies.value)
    try:
        current_last_visited_str = viewed.get(str(image_id))
        if current_last_visited_str:
            current_last_visited = datetime.datetime.strptime(current_last_visited_str, '%Y-%m-%d %H:%M:%S.%f')
            current_last_visited_one_day = current_last_visited + datetime.timedelta(days=1)
        if not current_last_visited_str or now > current_last_visited_one_day:
            db_images.patch_one(image_id, now_str)
            viewed[str(image_id)] = now_str
    except:
        print('error with datetime on image details.')
    viewed = json.dumps(viewed, default=default_converter)
    expires = datetime.datetime.utcnow() + datetime.timedelta(days=365)
    expires = expires.strftime('%a, %d %b %Y %H:%M:%S GMT')
    cookies['viewed'] = viewed
    cookies['viewed']['expires'] = expires
    cookies['viewed']['path'] = '/'
    context = dict()
    image_details = db_images.get_one(image_id)
    context['image_id'] = image_details['image_id']
    context['counter'] = image_details['counter']
    context['path'] = image_details['path']
    context['page_title'] = 'Image Details'
    send_file(client, 'pages/image-details.html', b'text/html', cookies, context)


@account_required(admin_required=True)
def delete_image(client: socket, cookies: SimpleCookie = None,
                 multipart_data: dict = None, image_id: int = None) -> None:
    context = dict()
    image_exists = db_images.get_one(image_id)
    if not image_exists:
        return redirect_to(client, b'/images/' + str(image_id).encode() + b'/details', cookies)
    db_images.delete_one(image_id)
    redirect_to(client, b'/', cookies)


@account_required()
def post_images_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    collection_id = multipart_data.get('selected-collection')
    image_contents = multipart_data.get('fimg')
    if not image_contents or not collection_id:
        return bad_request(client)
    collection_id = int(collection_id[0])
    image_contents = image_contents[0]
    collection = db_collections.get_one(collection_id)
    if not collection:
        return redirect_to(client, b'/', cookies)
    file_io = BytesIO(image_contents)
    directory = os.path.join(db_collections.COLLECTIONS_DIR, collection['name'])
    if not os.path.exists(directory):
        os.makedirs(directory)
    file_name = os.urandom(16).hex()
    file_type = imghdr.what(file_io)
    if file_type not in db_images.ALLOWED_FILE_TYPES:
        return redirect_to(client, b'/', cookies)
    full_path = os.path.join(directory, file_name + '.' + file_type).replace("\\", "/")
    try:
        with open(full_path, 'wb') as file:
            file.write(image_contents)
        db_images.insert_one(full_path.replace("\\", "/"), collection_id)
    except:
        print("Couldn't write to file.")
    redirect_to(client, b'/', cookies)


@account_required()
def get_settings_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    context = dict()
    context['page_title'] = 'Settings'
    send_file(client, 'pages/settings.html', b'text/html', cookies, context)


@account_required()
def post_settings_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    new_password = multipart_data.get('new-password')[0]
    repeat_new_password = multipart_data.get('repeat-new-password')[0]
    if len(new_password) < 8 or repeat_new_password != new_password:
        redirect_to(client, b'/settings', cookies)

    user = db_users.get_one_with_session_hash(cookies.get('sessId').coded_value)
    salt = bytes.fromhex(user['salt'])
    pw_hash = bytes.fromhex(user['password_hash'])
    old_password = multipart_data.get('old-password')[0]
    if not hashing.is_correct_password(salt, pw_hash, old_password):
        redirect_to(client, b'/settings', cookies)

    new_salt, new_pw_hash = hashing.hash_new_password(new_password)
    user_id = user['user_id']
    db_users.update_password(user_id, new_salt, new_pw_hash)


@redirect_if_logged_in
def get_signup_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    context = dict()
    context['page_title'] = 'Sign Up'
    send_file(client, 'pages/signup.html', b'text/html', cookies, context)


@redirect_if_logged_in
def get_login_page(client: socket, cookies: SimpleCookie, multipart_data: dict = None) -> None:
    context = dict()
    context['page_title'] = 'Log In'
    send_file(client, 'pages/login.html', b'text/html', cookies, context)


@redirect_if_logged_in
def post_login_page(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None) -> None:
    username = multipart_data['username'][0]
    user = db_users.get_one_with_username(username)
    if not user:
        return redirect_to(client, b'/login')

    salt = bytes.fromhex(user['salt'])
    pw_hash = bytes.fromhex(user['password_hash'])
    password = multipart_data['password'][0]
    if not hashing.is_correct_password(salt, pw_hash, password):
        return redirect_to(client, b'/login')

    user_id = user['user_id']
    valid_until = str(datetime.datetime.now() + datetime.timedelta(days=7))
    session_hash = hashing.session_token()
    cookies = SimpleCookie()
    cookies['sessId'] = session_hash
    cookies['sessId']['httponly'] = 'HttpOnly'
    cookies['sessId']['path'] = '/'
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


@account_required()
def post_image(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None) -> None:
    # TODO process post request
    redirect_to(client, b'/', cookies)


@account_required()
def post_collection(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None) -> None:
    name = multipart_data.get('collection-name')
    if name:
        name = name[0]
        if name.strip():
            db_collections.insert_one(name)

    redirect_to(client, b'/', cookies)


@account_required()
def post_logout(client: socket, cookies: SimpleCookie = None, multipart_data: dict = None) -> None:
    session_hash = cookies['sessId'].coded_value
    db_sessions.delete_one(session_hash)

    redirect_to(client, b'/login', cookies)
