import socket
# import threading

import HttpRequest

HOST = '127.0.0.1'
PORT = 8080

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen(5)

CRLF = b"\r\n"

while True:
    client, address = server.accept()
    print(f"Connected to client: {address}\n\n")

    request = client.recv(1024)
    req = HttpRequest.HttpRequest(request)

    contentLength = req.get_content_length()
    leftToReceive = contentLength - req.get_body_len()
    print("left to receive: ", leftToReceive)
    while leftToReceive > 0:
        chunk = client.recv(1024)
        req.concatenate_body(chunk)
        leftToReceive = contentLength - req.get_body_len()

    path = req.get_path()

    match path:
        case b'/favicon.ico':
            faviconFile = open("favicon.ico", "rb")
            faviconBinary = faviconFile.read()
            faviconFile.close()

            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += b"Content-Type: image/x-icon" + CRLF
            sendMsg += CRLF
            sendMsg += faviconBinary

            client.send(sendMsg)
        case b'/brad-pitt':
            imageFile = open("brad-pitt.jpg", "rb")
            imageBinary = imageFile.read()
            imageFile.close()

            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += b"Content-Type: image/jpeg" + CRLF
            sendMsg += CRLF
            sendMsg += imageBinary

            client.send(sendMsg)
        case b'/post':
            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += CRLF
            sendMsg += b"<h1>" + b'\n'.join(req.get_body().split(req.get_multipart_boundary())) + b"</h1>"
            client.send(sendMsg)
        case _:
            sendMsg = b"HTTP/1.1 404 Not Found" + CRLF
            sendMsg += b"Content-Type: text/html" + CRLF
            sendMsg += CRLF

            file = open("form.html", "rb")
            fileContents = file.read()
            file.close()

            sendMsg += fileContents
            client.send(sendMsg)

    client.close()
