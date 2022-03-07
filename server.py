import socket
import threading
import os

import HttpRequest

HOST = '127.0.0.1'
PORT = 8090

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server.bind((HOST, PORT))
server.listen(5)

CRLF = b"\r\n"

while True:
    client, address = server.accept()
    print(f"Connected to client: {address}\n\n")

    req = HttpRequest.HttpRequest(client)

    path = req.get_path()
    match path:
        case b'/favicon.ico':
            with open("favicon.ico", "rb") as file:
                fileContents = file.read()
            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += b"Content-Type: image/x-icon" + CRLF
            sendMsg += CRLF
            sendMsg += fileContents

            client.send(sendMsg)
        case b'/style.css':
            with open("style.css", "rb") as file:
                fileContents = file.read()

            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += b"Content-Type: text/css" + CRLF
            sendMsg += CRLF
            sendMsg += fileContents

            client.send(sendMsg)
        case b'/script.js':
            with open("script.js", "rb") as file:
                fileContents = file.read()

            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += b"Content-Type: text/javascript" + CRLF
            sendMsg += CRLF
            sendMsg += fileContents

            client.send(sendMsg)
        case b'/':
            with open("main.html", "rb") as file:
                fileContents = file.read()
            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += b"Content-Type: text/html" + CRLF
            sendMsg += b"Set-Cookie: sessId=1234; HttpOnly" + CRLF
            sendMsg += b"Set-Cookie: seen=image" + CRLF
            sendMsg += CRLF
            sendMsg += fileContents

            client.send(sendMsg)
        case b'/post':
            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += b"Content-Type: text/html" + CRLF
            sendMsg += CRLF
            sendMsg += b"<h1> success </h1>"
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
        case b'/404.png':
            imageFile = open("404.png", "rb")
            imageBinary = imageFile.read()
            imageFile.close()

            sendMsg = b"HTTP/1.1 200 OK" + CRLF
            sendMsg += b"Content-Type: image/jpeg" + CRLF
            sendMsg += CRLF
            sendMsg += imageBinary

            client.send(sendMsg)
        case _:
            sendMsg = b"HTTP/1.1 404 Not Found" + CRLF
            sendMsg += b"Content-Type: text/html" + CRLF
            sendMsg += CRLF

            file = open("404.html", "rb")
            fileContents = file.read()
            file.close()

            sendMsg += fileContents
            client.send(sendMsg)

    client.close()
