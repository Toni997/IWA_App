import cgi
import socket
from io import BytesIO
import http.cookies


class HttpRequest:
    def __init__(self, client: socket):
        self.client: socket = client
        self.header: dict | None = None
        self.body: bytes = b''
        self.cookies: dict | None = None

        self.__receive_all()
        self.__parse_cookies()

        content_type = self.get_content_type()
        if not content_type:
            return
        if content_type.find(b'multipart/form-data') != -1:
            fp = BytesIO(self.body)
            pdict = dict()
            pdict['boundary'] = self.get_multipart_boundary()
            form = cgi.parse_multipart(fp=fp, pdict=pdict)
            print(form)

    def __receive_all(self):
        # assuming header is not longer than 2048 bytes (fix later?)
        request = self.client.recv(2048)
        self.__parse_request(request)

        content_length = self.get_content_length()
        left_to_receive = content_length - self.get_body_len()
        while left_to_receive > 0:
            chunk = self.client.recv(1024)
            self.concatenate_body(chunk)
            left_to_receive -= len(chunk)

    def __parse_request(self, request) -> None:
        self.header = request.split(b'\r\n\r\n', 1)
        self.body = self.header[1] if len(self.header) > 1 else b''
        self.header = self.header[0].split(b'\r\n')
        req = self.header.pop(0).split()
        self.header = dict(x.split(b': ') for x in self.header)
        if len(req) <= 1:
            return
        self.header[b'Method'] = req[0]
        self.header[b'Path'] = req[1]
        self.header[b'Protocol'] = req[2]

    def __parse_cookies(self) -> None:
        self.cookies = self.header.get(b'Cookie')
        if not self.cookies:
            return
        # print('simple cookie - ', http.cookies.SimpleCookie(self.cookies.decode('utf-8')))
        self.cookies = self.cookies.split(b'; ')
        self.cookies = dict(x.split(b'=') for x in self.cookies)

    def get_header(self) -> dict | None:
        return self.header

    def get_body(self) -> bytes:
        return self.body

    def get_cookies(self) -> dict | None:
        return self.cookies

    def get_path(self) -> bytes | None:
        return self.header.get(b'Path')

    def get_content_length(self) -> int | None:
        content_length = self.header.get(b'Content-Length')
        return int(content_length.decode("utf-8")) if content_length else 0

    def get_content_type(self) -> bytes | None:
        return self.header.get(b'Content-Type')

    def get_multipart_boundary(self) -> bytes:
        if not self.header or not self.header.get(b'Content-Type'):
            return b''
        content_type = self.header.get(b'Content-Type').split(b'boundary=')
        if len(content_type) <= 1:
            return b''
        return content_type[1]

    def concatenate_body(self, text: bytes) -> None:
        self.body += text

    def get_body_len(self) -> int:
        return len(self.body)
