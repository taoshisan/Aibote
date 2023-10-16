import time

from AiBot import WebBotMain


class CustomWebScript(WebBotMain):
    log_level = "DEBUG"

    def script_main(self):
        self.goto("https://www.qq.com")
        time.sleep(2)
        self.new_page("https://www.baidu.com")
        time.sleep(2)
        self.set_element_value("//*[@id='kw']", "RPA_办公自动化—Aibote")
        time.sleep(2)
        result = self.execute_script('(()=>"aibote rpa")()')
        print(result)  # aibote rpa


if __name__ == '__main__':
    # 监听 6666 号端口
    driver_params = {
        "browserName": "chrome",
        "debugPort": 15120,  # 要接管的浏览器端口号
        "userDataDir": "./UserData",
        "browserPath": None,
        "argument": None,
    }
    CustomWebScript.execute(9999, driver_params=driver_params)
