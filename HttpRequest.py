class HttpRequest:
    def __init__(self, request: bytes):
        self.request = request
        self.header: dict | None = None
        self.body: bytes = b''
        self.cookies: dict | None = None

        self.__parse_request()
        self.__parse_cookies()

    def __parse_request(self) -> None:
        self.header = self.request.split(b'\r\n\r\n', 1)
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
        self.cookies = self.header.get('Cookie')
        if not self.cookies:
            return
        self.cookies = self.cookies.split('; ')
        self.cookies = dict(x.split('=') for x in self.cookies)

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

    def get_multipart_boundary(self) -> bytes:
        if not self.header or not self.header.get(b'Content-Type'):
            return b''
        content_type = self.header.get(b'Content-Type').split(b'boundary=')
        if len(content_type) <= 1:
            return b''
        return content_type[1]

    def concatenate_body(self, concat: bytes) -> None:
        self.body += concat

    def get_body_len(self) -> int:
        return len(self.body)
