import cgi
import socket
from io import BytesIO
from http.cookies import SimpleCookie


class HttpRequest:
    def __init__(self, client: socket):
        self.__client: socket = client
        self.__header: dict | None = None
        self.__body: bytes = b''
        self.__cookies: SimpleCookie | None = None
        self.__multipart_data = None

        self.__receive_all()
        self.__parse_multipart()
        self.__parse_cookies()

    def __receive_all(self):
        # assuming header is not longer than 2048 bytes (fix later?)
        request = self.__client.recv(2048)
        self.__parse_request(request)

        content_length = self.get_content_length()
        left_to_receive = content_length - self.get_body_len()
        while left_to_receive > 0:
            chunk = self.__client.recv(1024)
            self.concatenate_body(chunk)
            left_to_receive -= len(chunk)

    def __parse_request(self, request) -> None:
        self.__header = request.split(b'\r\n\r\n', 1)
        self.__body = self.__header[1] if len(self.__header) > 1 else b''
        self.__header = self.__header[0].split(b'\r\n')
        req = self.__header.pop(0).split()
        self.__header = dict(x.split(b': ') for x in self.__header)
        if len(req) < 3:
            return
        self.__header[b'Method'] = req[0]
        self.__header[b'Path'] = req[1]
        self.__header[b'Protocol'] = req[2]

    def __parse_multipart(self):
        content_type = self.get_content_type()
        if not content_type or content_type.find(b'multipart/form-data') == -1:
            return
        fp = BytesIO(self.__body)
        pdict = dict()
        pdict['boundary'] = self.get_multipart_boundary()
        self.__multipart_data = cgi.parse_multipart(fp=fp, pdict=pdict)

    def __parse_cookies(self) -> None:
        self.__cookies = self.__header.get(b'Cookie')
        if not self.__cookies:
            return
        self.cookies = SimpleCookie()
        self.cookies.load(self.__cookies.decode('utf-8'))

    def get_header(self) -> dict | None:
        return self.__header

    def get_body(self) -> bytes:
        return self.__body

    def get_cookies(self) -> SimpleCookie | None:
        return self.__cookies

    def get_path(self) -> bytes | None:
        return self.__header.get(b'Path')

    def get_content_length(self) -> int | None:
        content_length = self.__header.get(b'Content-Length')
        return int(content_length.decode("utf-8")) if content_length else 0

    def get_content_type(self) -> bytes | None:
        return self.__header.get(b'Content-Type')

    def get_multipart_boundary(self) -> bytes:
        if not self.__header or not self.__header.get(b'Content-Type'):
            return b''
        content_type = self.__header.get(b'Content-Type').split(b'boundary=')
        if len(content_type) <= 1:
            return b''
        return content_type[1]

    def get_multipart_data(self):
        return self.__multipart_data

    def concatenate_body(self, text: bytes) -> None:
        self.__body += text

    def get_body_len(self) -> int:
        return len(self.__body)
