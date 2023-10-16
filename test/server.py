import socketserver


class ThreadingTCPServerPlus(socketserver.ThreadingTCPServer):
    daemon_threads = True


class MyTCPHandler(socketserver.BaseRequestHandler):

    def handle(self) -> None:
        print("客户端: ", self.client_address)
        try:
            while True:
                data = self.request.recv(1024)
                data_str = data.decode("utf8")
                print(data_str)
                msg = "我收到了：" + data_str
                self.request.sendall(msg.encode("utf8"))
        except ConnectionAbortedError:
            print(f"{self.client_address} 连接中断...")


if __name__ == '__main__':
    HOST, PORT = "0.0.0.0", 9999

    with ThreadingTCPServerPlus((HOST, PORT), MyTCPHandler) as server:
        # 激活服务器；
        # 它将一直运行，直到使用 Ctrl-C 组合键中断程序
        server.serve_forever()
