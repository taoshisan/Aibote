import socket
import time

HOST = "localhost"
PORT = 9999

address_info = socket.getaddrinfo(HOST, PORT, socket.AF_INET, socket.SOCK_STREAM)[0]

family, socket_type, proto, _, socket_address = address_info

while True:
    try:
        sock = socket.socket(family, socket_type, proto)
        sock.connect(socket_address)

        with sock:
            while True:
                msg = "Hello World!"
                n = sock.send(msg.encode("utf8"))
                print(f'Send: {n} bytes', )

                time.sleep(1)
                data = sock.recv(1024)
                print(f'Received: ', data.decode("utf8"))
                time.sleep(5)
    except Exception as e:
        print(e)
