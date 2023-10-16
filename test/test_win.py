import time

from AiBot import WinBotMain


class CustomWinScript(WinBotMain):
    log_level = "DEBUG"

    def script_main(self):
        print(111)
        result = self.find_windows()
        print(result)

        while True:
            time.sleep(5)
            print(666)


if __name__ == '__main__':
    # 监听 6666 号端口
    CustomWinScript.execute(6666)
