import abc
import socket
import socketserver
import subprocess
import sys
import threading
import time
import re
from ast import literal_eval
from typing import Optional, List, Tuple, Union

from loguru import logger

from ._utils import _protect, Point, _Region, _Algorithm, _SubColors
from urllib import request, parse
import json
import base64

class Point:
    def __init__(self, x: float, y: float, driver: "WinBotMain"):
        self.x = x
        self.y = y
        self.__driver = driver

    def click(self, offset_x: float = 0, offset_y: float = 0):
        """
        点击坐标

        :param offset_x: 坐标 x 轴偏移量
        :param offset_y: 坐标 y 轴偏移量
        :return:
        """
        return self.__driver.click(self, offset_x=offset_x, offset_y=offset_y)

    def get_points_center(self, other_point: "Point") -> "Point":
        """
        获取两个坐标点的中间坐标

        :param other_point: 其他的坐标点
        :return: Point
        """
        return self.__class__(x=self.x + (other_point.x - self.x) / 2, y=self.y + (other_point.y - self.y) / 2,
                              driver=self.__driver)

    def __getitem__(self, item):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError("list index out of range")

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"

_Point_Tuple = Union[Point, Tuple[float, float]]

class _ThreadingTCPServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True


class WinBotMain(socketserver.BaseRequestHandler, metaclass=_protect("handle", "execute")):
    raise_err = False

    wait_timeout = 3  # seconds
    interval_timeout = 0.5  # seconds

    log_path = ""
    log_level = "INFO"
    log_format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
                 "<level>{level: <8}</level> | " \
                 "{thread.name: <8} | " \
                 "<cyan>{module}.{function}:{line}</cyan> | " \
                 "<level>{message}</level>"  # 日志内容

    def __init__(self, request, client_address, server):
        self._lock = threading.Lock()
        self.log = logger

        self.log.remove()
        self.log.add(sys.stdout, level=self.log_level.upper(), format=self.log_format)

        if self.log_path:
            self.log.add(self.log_path, level=self.log_level.upper(), format=self.log_format,
                         rotation='5 MB', retention='2 days')

        super().__init__(request, client_address, server)

    def __send_data(self, *args) -> str:
        args_len = ""
        args_text = ""

        for argv in args:
            if argv is None:
                argv = ""
            elif isinstance(argv, bool) and argv:
                argv = "true"
            elif isinstance(argv, bool) and not argv:
                argv = "false"

            argv = str(argv)
            args_text += argv
            args_len += str(len(bytes(argv, 'utf8'))) + "/"

        data = (args_len.strip("/") + "\n" + args_text).encode("utf8")

        try:
            with self._lock:
                self.log.debug(rf"->-> {data}")
                self.request.sendall(data)
                response = self.request.recv(65535)
                if response == b"":
                    raise ConnectionAbortedError(f"{self.client_address[0]}:{self.client_address[1]} 客户端断开链接。")
                data_length, data = response.split(b"/", 1)
                while int(data_length) > len(data):
                    data += self.request.recv(65535)
                self.log.debug(rf"<-<- {data}")

            return data.decode("utf8").strip()
        except Exception as e:
            self.log.error("send/read tcp data error: " + str(e))
            raise e

    # #############
    #   窗口操作   #
    # #############
    def find_window(self, class_name: str = None, window_name: str = None) -> Optional[str]:
        """
        查找窗口句柄，仅查找顶级窗口，不包含子窗口

        :param class_name: 窗口类名
        :param window_name: 窗口名
        :return:
        """
        response = self.__send_data("findWindow", class_name, window_name)
        if response == "null":
            return None
        return response

    def find_windows(self, class_name: str = None, window_name: str = None) -> List[str]:
        """
        查找窗口句柄数组，仅查找顶级窗口，不包含子窗口

        class_name 和 window_name 都为 None，则返回所有窗口句柄

        :param class_name: 窗口类名
        :param window_name: 窗口名
        :return: 窗口句柄的列表
        """
        response = self.__send_data("findWindows", class_name, window_name)
        if response == "null":
            return []
        return response.split("|")

    def find_sub_window(self, hwnd: str, class_name: str = None, window_name: str = None) -> Optional[str]:
        """
        查找子窗口句柄

        :param hwnd: 当前窗口句柄
        :param class_name: 窗口类名
        :param window_name: 窗口名
        :return: 子窗口句柄或 None
        """
        response = self.__send_data("findSubWindow", hwnd, class_name, window_name)
        if response == "null":
            return None
        return response

    def find_parent_window(self, hwnd: str) -> Optional[str]:
        """
        查找父窗口句柄

        :param hwnd: 当前窗口句柄
        :return: 父窗口句柄或 None
        """
        response = self.__send_data("findParentWindow", hwnd)
        if response == "null":
            return None
        return response

    def find_desktop_window(self) -> Optional[str]:
        """
        查找桌面窗口句柄

        :return: 桌面窗口句柄或 None
        """
        response = self.__send_data("findDesktopWindow")
        if response == "null":
            return None
        return response

    def get_window_name(self, hwnd: str) -> Optional[str]:
        """
        获取窗口名称

        :param hwnd: 当前窗口句柄
        :return: 窗口名称或 None
        """
        response = self.__send_data("getWindowName", hwnd)
        if response == "null":
            return None
        return response

    def show_window(self, hwnd: str, show: bool) -> bool:
        """
        显示/隐藏窗口

        :param hwnd: 当前窗口句柄
        :param show: 是否显示窗口
        :return:
        """
        return self.__send_data("showWindow", hwnd, show) == "true"

    def set_window_top(self, hwnd: str, top: bool) -> bool:
        """
        设置窗口到最顶层

        :param hwnd: 当前窗口句柄
        :param top: 是否置顶，True 置顶， False 取消置顶
        :return:
        """
        return self.__send_data("setWindowTop", hwnd, top) == "true"

    def get_window_pos(self, hwnd: str, wait_time: float = None, interval_time: float = None) -> Optional[
        Tuple[Point, Point]]:
        """
        获取窗口位置

        :param hwnd: 窗口句柄
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("getWindowPos", hwnd)
            if response == "-1|-1|-1|-1":
                time.sleep(interval_time)
                continue
            else:
                x1, y1, x2, y2 = response.split("|")
                return Point(x=float(x1), y=float(y1)), Point(x=float(x2), y=float(y2))
        # 超时
        return None

    def set_window_pos(self, hwnd: str, left: float, top: float, width: float, height: float) -> bool:
        """
        设置窗口位置

        :param hwnd: 当前窗口句柄
        :param left: 左上角横坐标
        :param top: 左上角纵坐标
        :param width: 窗口宽度
        :param height: 窗口高度
        :return:
        """
        return self.__send_data("setWindowPos", hwnd, left, top, width, height) == "true"

    # #############
    #   键鼠操作   #
    # #############
    def move_mouse(self, hwnd: str, x: float, y: float, mode: bool = False, ele_hwnd: str = "0") -> bool:
        """
        移动鼠标

        :param hwnd: 当前窗口句柄
        :param x: 横坐标
        :param y: 纵坐标
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作
        :param ele_hwnd: 元素句柄，如果 mode=True 且目标控件有单独的句柄，则需要通过 get_element_window 获得元素句柄，指定 ele_hwnd 的值(极少应用窗口由父窗口响应消息，则无需指定);
        :return:
        """
        return self.__send_data("moveMouse", hwnd, x, y, mode, ele_hwnd) == "true"

    def move_mouse_relative(self, hwnd: str, x: float, y: float, mode: bool = False) -> bool:
        """
        移动鼠标(相对坐标)

        :param hwnd: 当前窗口句柄
        :param x: 相对横坐标
        :param y: 相对纵坐标
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作
        :return:
        """
        return self.__send_data("moveMouseRelative", hwnd, x, y, mode) == "true"

    def scroll_mouse(self, hwnd: str, x: float, y: float, count: int, mode: bool = False) -> bool:
        """
        滚动鼠标

        :param hwnd: 当前窗口句柄
        :param x: 横坐标
        :param y: 纵坐标
        :param count: 鼠标滚动次数, 负数下滚鼠标, 正数上滚鼠标
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作
        :return:
        """
        return self.__send_data("rollMouse", hwnd, x, y, count, mode) == "true"

    def click_mouse(self, hwnd: str, x: float, y: float, typ: int, mode: bool = False, ele_hwnd: str = "0") -> bool:
        """
        鼠标点击

        :param hwnd: 当前窗口句柄
        :param x: 横坐标
        :param y: 纵坐标
        :param typ: 点击类型，单击左键:1 单击右键:2 按下左键:3 弹起左键:4 按下右键:5 弹起右键:6 双击左键:7 双击右键:8
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作
        :param ele_hwnd: 元素句柄，如果 mode=True 且目标控件有单独的句柄，则需要通过 get_element_window 获得元素句柄，指定 ele_hwnd 的值(极少应用窗口由父窗口响应消息，则无需指定);
        :return:
        """
        return self.__send_data("clickMouse", hwnd, x, y, typ, mode, ele_hwnd) == "true"

    def send_keys(self, text: str) -> bool:
        """
        输入文本

        :param text: 输入的文本
        :return:
        """
        return self.__send_data("sendKeys", text) == "true"

    def send_keys_by_hwnd(self, hwnd: str, text: str) -> bool:
        """
        后台输入文本(杀毒软件可能会拦截)

        :param hwnd: 窗口句柄
        :param text: 输入的文本
        :return:
        """
        return self.__send_data("sendKeysByHwnd", hwnd, text) == "true"

    def send_vk(self, vk: int, typ: int) -> bool:
        """
        输入虚拟键值(VK)

        :param vk: VK键值
        :param typ: 输入类型，按下弹起:1 按下:2 弹起:3
        :return:
        """
        return self.__send_data("sendVk", vk, typ) == "true"

    def send_vk_by_hwnd(self, hwnd: str, vk: int, typ: int) -> bool:
        """
        后台输入虚拟键值(VK)

        :param hwnd: 窗口句柄
        :param vk: VK键值
        :param typ: 输入类型，按下弹起:1 按下:2 弹起:3
        :return:
        """
        return self.__send_data("sendVkByHwnd", hwnd, vk, typ) == "true"

    # #############
    #   图色操作   #
    # #############
    def save_screenshot(self, hwnd: str, save_path: str, region: _Region = None, algorithm: _Algorithm = None,
                        mode: bool = False) -> bool:
        """
        截图

        :param hwnd: 窗口句柄
        :param save_path: 图片存储路径
        :param region: 截图区域，默认全屏，``region = (起点x、起点y、终点x、终点y)``，得到一个矩形
        :param algorithm:
            处理截图所用算法和参数，默认保存原图，

            ``algorithm = (algorithm_type, threshold, max_val)``

            按元素顺序分别代表：

            0. ``algorithm_type`` 算法类型
            1. ``threshold`` 阈值
            2. ``max_val`` 最大值

            ``threshold`` 和 ``max_val`` 同为 255 时灰度处理.

            ``algorithm_type`` 算法类型说明:

            0. ``THRESH_BINARY``      算法，当前点值大于阈值 `threshold` 时，取最大值 ``max_val``，否则设置为 0；
            1. ``THRESH_BINARY_INV``  算法，当前点值大于阈值 `threshold` 时，设置为 0，否则设置为最大值 max_val；
            2. ``THRESH_TOZERO``      算法，当前点值大于阈值 `threshold` 时，不改变，否则设置为 0；
            3. ``THRESH_TOZERO_INV``  算法，当前点值大于阈值 ``threshold`` 时，设置为 0，否则不改变；
            4. ``THRESH_TRUNC``       算法，当前点值大于阈值 ``threshold`` 时，设置为阈值 ``threshold``，否则不改变；
            5. ``ADAPTIVE_THRESH_MEAN_C``      算法，自适应阈值；
            6. ``ADAPTIVE_THRESH_GAUSSIAN_C``  算法，自适应阈值；

        :param mode: 操作模式，后台 true，前台 false, 默认前台操作
        :return:

        """
        if not region:
            region = [0, 0, 0, 0]

        if not algorithm:
            algorithm_type, threshold, max_val = [0, 0, 0]
        else:
            algorithm_type, threshold, max_val = algorithm
            if algorithm_type in (5, 6):
                threshold = 127
                max_val = 255

        return self.__send_data("saveScreenshot", hwnd, save_path, *region, algorithm_type, threshold, max_val,
                                mode) == "true"

    def get_color(self, hwnd: str, x: float, y: float, mode: bool = False) -> Optional[str]:
        """
        获取指定坐标点的色值，返回色值字符串(#008577)或者 None

        :param hwnd: 窗口句柄；
        :param x: x 坐标；
        :param y: y 坐标；
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
        :return:
        """
        response = self.__send_data("getColor", hwnd, x, y, mode)
        if response == "null":
            return None
        return response

    def find_color(self, hwnd: str, color: str, sub_colors: _SubColors = None, region: _Region = None,
                   similarity: float = 0.9, mode: bool = False, wait_time: float = None,
                   interval_time: float = None):
        """
        获取指定色值的坐标点，返回坐标或者 None

        :param hwnd: 窗口句柄；
        :param color: 颜色字符串，必须以 # 开头，例如：#008577；
        :param sub_colors: 辅助定位的其他颜色；
        :param region: 在指定区域内找色，默认全屏；
        :param similarity: 相似度，0-1 的浮点数，默认 0.9；
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:

        .. seealso::
            :meth:`save_screenshot`: ``region`` 和 ``algorithm`` 的参数说明

        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if not region:
            region = [0, 0, 0, 0]

        if sub_colors:
            sub_colors_str = ""
            for sub_color in sub_colors:
                offset_x, offset_y, color_str = sub_color
                sub_colors_str += f"{offset_x}/{offset_y}/{color_str}\n"
            # 去除最后一个 \n
            sub_colors_str = sub_colors_str.strip()
        else:
            sub_colors_str = "null"

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("findColor", hwnd, color, sub_colors_str, *region, similarity, mode)
            # 找色失败
            if response == "-1.0|-1.0":
                time.sleep(interval_time)
            else:
                # 找色成功
                x, y = response.split("|")
                return Point(x=float(x), y=float(y))
        # 超时
        return None

    def compare_color(self,
                      hwnd: str,
                      main_x: float,
                      main_y: float,
                      color: str,
                      sub_colors: _SubColors = None,
                      region: _Region = None,
                      similarity: float = 0.9,
                      mode: bool = False,
                      wait_time: float = None,
                      interval_time: float = None,
                      raise_err: bool = None) -> Optional[Point]:
        """
        比较指定坐标点的颜色值

        :param hwnd: 窗口句柄；
        :param main_x: 主颜色所在的X坐标；
        :param main_y: 主颜色所在的Y坐标；
        :param color: 颜色字符串，必须以 # 开头，例如：#008577；
        :param sub_colors: 辅助定位的其他颜色；
        :param region: 截图区域，默认全屏，``region = (起点x、起点y、终点x、终点y)``，得到一个矩形
        :param similarity: 相似度，0-1 的浮点数，默认 0.9；
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :param raise_err: 超时是否抛出异常；
        :return: True或者 False

        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

        if not region:
            region = [0, 0, 0, 0]

        if sub_colors:
            sub_colors_str = ""
            for sub_color in sub_colors:
                offset_x, offset_y, color_str = sub_color
                sub_colors_str += f"{offset_x}/{offset_y}/{color_str}\n"
            # 去除最后一个 \n
            sub_colors_str = sub_colors_str.strip()
        else:
            sub_colors_str = "null"

        end_time = time.time() + wait_time
        while time.time() < end_time:
            return self.__send_data("compareColor", hwnd, main_x, main_y, color, sub_colors_str, *region, similarity,
                                    mode) == "true"
        # 超时
        if raise_err:
            raise TimeoutError("`compare_color` 操作超时")
        return None

    def extract_image_by_video(self, video_path: str, save_folder: str, jump_frame: int = 1) -> bool:
        """
        提取视频帧

        :param video_path: 视频路径
        :param save_folder: 提取的图片保存的文件夹目录
        :param jump_frame: 跳帧，默认为1 不跳帧
        :return: True或者False
        """
        return self.__send_data("extractImageByVideo", video_path, save_folder, jump_frame) == "true"

    def crop_image(self, image_path, save_path, left, top, rigth, bottom) -> bool:
        """
        裁剪图片

        :param image_path: 图片路径
        :param save_path: 裁剪后保存的图片路径
        :param left: 裁剪的左上角横坐标
        :param top: 裁剪的左上角纵坐标
        :param rigth: 裁剪的右下角横坐标
        :param bottom: 裁剪的右下角纵坐标
        :return: True或者False
        """
        return self.__send_data("cropImage", image_path, save_path, left, top, rigth, bottom) == "true"

    def find_images(self, hwnd: str, image_path: str, region: _Region = None, algorithm: _Algorithm = None,
                    similarity: float = 0.9, mode: bool = False, multi: int = 1, wait_time: float = None,
                    interval_time: float = None) -> List[Point]:
        """
        寻找图片坐标，在当前屏幕中寻找给定图片中心点的坐标，返回坐标列表

        :param hwnd: 窗口句柄；
        :param image_path: 图片的绝对路径；
        :param region: 从指定区域中找图，默认全屏；
        :param algorithm: 处理屏幕截图所用的算法，默认原图，注意：给定图片处理时所用的算法，应该和此方法的算法一致；
        :param similarity: 相似度，0-1 的浮点数，默认 0.9；
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
        :param multi: 返回图片数量，默认1张；
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:

        .. seealso::
            :meth:`save_screenshot`: ``region`` 和 ``algorithm`` 的参数说明

        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if not region:
            region = [0, 0, 0, 0]

        if not algorithm:
            algorithm_type, threshold, max_val = [0, 0, 0]
        else:
            algorithm_type, threshold, max_val = algorithm
            if algorithm_type in (5, 6):
                threshold = 127
                max_val = 255

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("findImage", hwnd, image_path, *region, similarity, algorithm_type,
                                        threshold, max_val, multi, mode)
            # 找图失败
            if response in ["-1.0|-1.0", "-1|-1"]:
                time.sleep(interval_time)
                continue
            else:
                # 找图成功，返回图片左上角坐标
                # 分割出多个图片的坐标
                image_points = response.split("/")
                point_list = []
                for point_str in image_points:
                    x, y = point_str.split("|")
                    point_list.append(Point(x=float(x), y=float(y)))
                return point_list
        # 超时
        return []

    def find_dynamic_image(self, hwnd: str, interval_ti: int, region: _Region = None, mode: bool = False,
                           wait_time: float = None, interval_time: float = None) -> List[Point]:
        """
        找动态图，对比同一张图在不同时刻是否发生变化，返回坐标列表

        :param hwnd: 窗口句柄；
        :param interval_ti: 前后时刻的间隔时间，单位毫秒；
        :param region: 在指定区域找图，默认全屏；
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:

        .. seealso::
            :meth:`save_screenshot`: ``region`` 的参数说明

        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if not region:
            region = [0, 0, 0, 0]

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("findAnimation", hwnd, interval_ti, *region, mode)
            # 找图失败
            if response == "-1.0|-1.0":
                time.sleep(interval_time)
                continue
            else:
                # 找图成功，返回图片左上角坐标
                # 分割出多个图片的坐标
                image_points = response.split("/")
                point_list = []
                for point_str in image_points:
                    x, y = point_str.split("|")
                    point_list.append(Point(x=float(x), y=float(y)))
                return point_list
        # 超时
        return []

    # ##############
    #   OCR 相关   #
    # ##############
    @staticmethod
    def __parse_ocr(text: str) -> list:
        """
        解析 OCR 识别出出来的信息

        :param text:
        :return:
        """
        # pattern = re.compile(r'(\[\[\[).+?(\)])')
        # matches = pattern.finditer(text)
        #
        # text_info_list = []
        # for match in matches:
        #     result_str = match.group()
        #     text_info = literal_eval(result_str)
        #     text_info_list.append(text_info)

        return literal_eval(text)

    def __ocr_server(self, hwnd: str, region: _Region = None, algorithm: _Algorithm = None, mode: bool = False) -> list:
        """
        OCR 服务，通过 OCR 识别屏幕中文字

        :param hwnd:
        :param region:
        :param algorithm:
        :param mode:
        :return:
        """
        if not region:
            region = [0, 0, 0, 0]

        if not algorithm:
            algorithm_type, threshold, max_val = [0, 0, 0]
        else:
            algorithm_type, threshold, max_val = algorithm
            if algorithm_type in (5, 6):
                threshold = 127
                max_val = 255

        response = self.__send_data("ocr", hwnd, *region, algorithm_type, threshold, max_val, mode)
        if response == "null" or response == "[]":
            return []
        return self.__parse_ocr(response)

    def __ocr_server_by_file(self, image_path: str, region: _Region = None, algorithm: _Algorithm = None) -> list:
        """
        OCR 服务，通过 OCR 识别屏幕中文字

        :param image_path:
        :param region:
        :param algorithm:
        :return:
        """
        if not region:
            region = [0, 0, 0, 0]

        if not algorithm:
            algorithm_type, threshold, max_val = [0, 0, 0]
        else:
            algorithm_type, threshold, max_val = algorithm
            if algorithm_type in (5, 6):
                threshold = 127
                max_val = 255

        response = self.__send_data("ocrByFile", image_path, *region, algorithm_type, threshold, max_val)
        if response == "null" or response == "[]":
            return []
        return self.__parse_ocr(response)

    def init_ocr_server(self, ip: str, port: int = 9752) -> bool:
        """
        初始化 OCR 服务

        :param ip:
        :param port:
        :return:
        """
        return self.__send_data("initOcr", ip, port) == "true"

    def get_text(self, hwnd_or_image_path: str, region: _Region = None, algorithm: _Algorithm = None,
                 mode: bool = False) -> List[str]:
        """
        通过 OCR 识别窗口/图片中的文字，返回文字列表

        :param hwnd_or_image_path: 窗口句柄或者图片路径；
        :param region: 识别区域，默认全屏；
        :param algorithm: 处理图片/屏幕所用算法和参数，默认保存原图；
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
        :return:

        .. seealso::
            :meth:`save_screenshot`: ``region`` 和 ``algorithm`` 的参数说明

        """
        if hwnd_or_image_path.isdigit():
            # 句柄
            text_info_list = self.__ocr_server(hwnd_or_image_path, region, algorithm, mode)
        else:
            # 图片
            text_info_list = self.__ocr_server_by_file(hwnd_or_image_path, region, algorithm)

        text_list = []
        for text_info in text_info_list:
            text = text_info[-1][0]
            text_list.append(text)
        return text_list

    def find_text(self, hwnd_or_image_path: str, text: str, region: _Region = None, algorithm: _Algorithm = None,
                  mode: bool = False) -> List[Point]:
        """
        通过 OCR 识别窗口/图片中的文字，返回文字列表

        :param hwnd_or_image_path: 句柄或者图片路径
        :param text: 要查找的文字
        :param region: 识别区域，默认全屏
        :param algorithm: 处理图片/屏幕所用算法和参数，默认保存原图
        :param mode: 操作模式，后台 true，前台 false, 默认前台操作
        :return: 文字列表

        .. seealso::
            :meth:`save_screenshot`: ``region`` 和 ``algorithm`` 的参数说明

        """
        if not region:
            region = [0, 0, 0, 0]

        if hwnd_or_image_path.isdigit():
            # 句柄
            text_info_list = self.__ocr_server(hwnd_or_image_path, region, algorithm, mode)
        else:
            # 图片
            text_info_list = self.__ocr_server_by_file(hwnd_or_image_path, region, algorithm)

        text_points = []
        for text_info in text_info_list:
            if text in text_info[-1][0]:
                points, words_tuple = text_info

                left, _, right, _ = points

                # 文本区域起点坐标
                start_x = left[0]
                start_y = left[1]
                # 文本区域终点坐标
                end_x = right[0]
                end_y = right[1]
                # 文本区域中心点据左上角的偏移量
                # 可能指定文本只是部分文本，要计算出实际位置(x轴)
                width = end_x - start_x
                height = end_y - start_y
                words: str = words_tuple[0]

                # 单字符宽度
                single_word_width = width / len(words)
                # 文本在整体文本的起始位置
                pos = words.find(text)

                offset_x = single_word_width * (pos + len(text) / 2)
                offset_y = height / 2

                # 计算文本区域中心坐标
                text_point = Point(
                    x=float(region[0] + start_x + offset_x),
                    y=float(region[1] + start_y + offset_y),
                )
                text_points.append(text_point)

        return text_points

    # ##############
    #   元素操作   #
    # ##############

    def get_element_name(self, hwnd: str, xpath: str, wait_time: float = None, interval_time: float = None) \
            -> Optional[str]:
        """
        获取元素名称

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return: 元素名称字符串或 None
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("getElementName", hwnd, xpath)
            if response == "null":
                time.sleep(interval_time)
                continue
            else:
                return response
        # 超时
        return None

    def get_element_value(self, hwnd: str, xpath: str, wait_time: float = None, interval_time: float = None) \
            -> Optional[str]:
        """
        获取元素文本

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return: 元素文本字符串或 None
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("getElementValue", hwnd, xpath)
            if response == "null":
                time.sleep(interval_time)
                continue
            else:
                return response
        # 超时
        return None

    def get_element_rect(self, hwnd: str, xpath: str, wait_time: float = None, interval_time: float = None) \
            -> Optional[Tuple[Point, Point]]:
        """
        获取元素矩形，返回左上和右下坐标

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return: 左上和右下坐标
        :rtype: Optional[Tuple[Point, Point]]
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("getElementRect", hwnd, xpath)
            if response == "-1|-1|-1|-1":
                time.sleep(interval_time)
                continue
            else:
                x1, y1, x2, y2 = response.split("|")
                return Point(x=float(x1), y=float(y1)), Point(x=float(x2), y=float(y2))
        # 超时
        return None

    def get_element_window(self, hwnd: str, xpath: str, wait_time: float = None, interval_time: float = None) \
            -> Optional[str]:
        """
        获取元素窗口句柄

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return: 元素窗口句柄字符串或 None
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("getElementWindow", hwnd, xpath)
            if response == "null":
                time.sleep(interval_time)
                continue
            else:
                return response
        # 超时
        return None

    def click_element(self, hwnd: str, xpath: str, typ: int, wait_time: float = None,
                      interval_time: float = None) -> bool:
        """
        点击元素

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param typ: 操作类型，单击左键:1 单击右键:2 按下左键:3 弹起左键:4 按下右键:5 弹起右键:6 双击左键:7 双击右键:8
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data('clickElement', hwnd, xpath, typ)
            if response == "false":
                time.sleep(interval_time)
                continue
            else:
                return True
        # 超时
        return False

    def invoke_element(self, hwnd: str, xpath: str, wait_time: float = None,
                       interval_time: float = None) -> bool:
        """
        执行元素默认操作(一般是点击操作)

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data('invokeElement', hwnd, xpath)
            if response == "false":
                time.sleep(interval_time)
                continue
            else:
                return True
        # 超时
        return False

    def set_element_focus(self, hwnd: str, xpath: str, wait_time: float = None,
                          interval_time: float = None) -> bool:
        """
        设置元素作为焦点

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data('setElementFocus', hwnd, xpath)
            if response == "false":
                time.sleep(interval_time)
                continue
            else:
                return True
        # 超时
        return False

    def set_element_value(self, hwnd: str, xpath: str, value: str,
                          wait_time: float = None, interval_time: float = None) -> bool:
        """
        设置元素文本

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param value: 要设置的内容
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data('setElementValue', hwnd, xpath, value)
            if response == "false":
                time.sleep(interval_time)
                continue
            else:
                return True
        # 超时
        return False

    def scroll_element(self, hwnd: str, xpath: str, horizontal: int, vertical: int,
                       wait_time: float = None, interval_time: float = None) -> bool:
        """
        滚动元素

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param horizontal: 水平百分比 -1不滚动
        :param vertical: 垂直百分比 -1不滚动
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data('setElementScroll', hwnd, xpath, horizontal, vertical)
            if response == "false":
                time.sleep(interval_time)
                continue
            else:
                return True
        # 超时
        return False

    def is_selected(self, hwnd: str, xpath: str,
                    wait_time: float = None, interval_time: float = None) -> bool:
        """
        单/复选框是否选中

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data('isSelected', hwnd, xpath)
            if response == "false":
                time.sleep(interval_time)
                continue
            else:
                return True
        # 超时
        return False

    def close_window(self, hwnd: str, xpath: str) -> bool:
        """
        关闭窗口

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :return:
        """
        return self.__send_data('closeWindow', hwnd, xpath) == 'true'

    def set_element_state(self, hwnd: str, xpath: str, state: str) -> bool:
        """
        设置窗口状态

        :param hwnd: 窗口句柄
        :param xpath: 元素路径
        :param state: 0正常 1最大化 2 最小化
        :return:
        """
        return self.__send_data('setWindowState', hwnd, xpath, state) == 'true'

    # ###############
    #   系统剪切板   #
    # ###############
    def set_clipboard_text(self, text: str) -> bool:
        """
        设置剪切板内容

        :param text: 要设置的内容
        :return:
        """
        return self.__send_data("setClipboardText", text) == 'true'

    def get_clipboard_text(self) -> str:
        """
        设置剪切板内容

        :return:
        """
        return self.__send_data("getClipboardText")

    # #############
    #   启动进程   #
    # #############

    def start_process(self, cmd: str, show_window=True, is_wait=False) -> bool:
        """
        执行cmd命令

        :param cmd: 命令
        :param show_window: 是否显示窗口，默认显示
        :param is_wait: 是否等待程序结束， 默认不等待
        :return:
        """
        return self.__send_data("startProcess", cmd, show_window, is_wait) == "true"

    def execute_command(self, command: str, waitTimeout: int = 300) -> str:
        """
        执行cmd命令

        :param command: cmd命令，不能含 "cmd"字串
        :param waitTimeout: 可选参数，等待结果返回超时，单位毫秒，默认300毫秒
        :return: cmd执行结果
        """
        return self.__send_data("executeCommand", command, waitTimeout)

    def download_file(self, url: str, file_path: str, is_wait: bool) -> bool:
        """
        下载文件

        :param url: 文件地址
        :param file_path: 文件保存的路径
        :param is_wait: 是否等待下载完成
        :return:
        """
        return self.__send_data("downloadFile", url, file_path, is_wait) == "true"

    # #############
    #  EXCEL操作  #
    # #############
    def open_excel(self, excel_path: str) -> Optional[dict]:
        """
        打开excel文档

        :param excel_path: excle路径
        :return: excel对象或者None
        """
        response = self.__send_data("openExcel", excel_path)
        if response == "null":
            return None
        return json.loads(response)

    def open_excel_sheet(self, excel_object: dict, sheet_name: str) -> Optional[dict]:
        """
        打开excel表格

        :param excel_object: excel对象
        :param sheet_name: 表名
        :return: sheet对象或者None
        """
        response = self.__send_data("openExcelSheet", excel_object['book'], excel_object['path'], sheet_name)
        if response == "null":
            return None
        return response

    def save_excel(self, excel_object: dict) -> bool:
        """
        保存excel文档

        :param excel_object: excel对象
        :return: True或者False
        """
        return self.__send_data("saveExcel", excel_object['book'], excel_object['path']) == "true"

    def write_excel_num(self, excel_object: dict, row: int, col: int, value: int) -> bool:
        """
        写入数字到excel表格

        :param excel_object: excel对象
        :param row: 行
        :param col: 列
        :param value: 写入的值
        :return: True或者False
        """
        return self.__send_data("writeExcelNum", excel_object, row, col, value) == "true"

    def write_excel_str(self, excel_object: dict, row: int, col: int, str_value: str) -> bool:
        """
        写入字符串到excel表格

        :param excel_object: excel对象
        :param row: 行
        :param col: 列
        :param str_value: 写入的值
        :return: True或者False
        """
        return self.__send_data("writeExcelStr", excel_object, row, col, str_value) == "true"

    def read_excel_num(self, excel_object: dict, row: int, col: int) -> int:
        """
        读取excel表格数字

        :param excel_object: excel对象
        :param row: 行
        :param col: 列
        :return: 读取到的数字
        """
        response = self.__send_data("readExcelNum", excel_object, row, col)
        return float(response)

    def read_excel_str(self, excel_object: dict, row: int, col: int) -> str:
        """
        读取excel表格字符串

        :param excel_object: excel对象
        :param row: 行
        :param col: 列
        :return: 读取到的字符
        """
        return self.__send_data("readExcelStr", excel_object, row, col)

    def remove_excel_row(self, excel_object: dict, row_first: int, row_last: int) -> bool:
        """
        删除excel表格行

        :param excel_object: excel对象
        :param row_first: 起始行
        :param row_last: 结束行
        :return: True或者False
        """
        return self.__send_data("removeExcelRow", excel_object, row_first, row_last) == "true"

    def remove_excel_col(self, excel_object: dict, col_first: int, col_last: int) -> bool:
        """
        删除excel表格列

        :param excel_object: excel对象
        :param col_first: 起始列
        :param col_last: 结束列
        :return: True或者False
        """
        return self.__send_data("removeExcelCol", excel_object, col_first, col_last) == "true"

    # ##########
    #  验证码  #
    ############
    def get_captcha(self, file_path: str, username: str, password: str, soft_id: str, code_type: str,
                    len_min: str = '0') -> Optional[dict]:
        """
        识别验证码

        :param file_path: 图片文件路径
        :param username: 用户名
        :param password: 密码
        :param soft_id: 软件ID
        :param code_type: 图片类型 参考https://www.chaojiying.com/price.html
        :param len_min: 最小位数 默认0为不启用,图片类型为可变位长时可启用这个参数
        :return: JSON
            err_no,(数值) 返回代码  为0 表示正常，错误代码 参考https://www.chaojiying.com/api-23.html
            err_str,(字符串) 中文描述的返回信息 
            pic_id,(字符串) 图片标识号，或图片id号
            pic_str,(字符串) 识别出的结果
            md5,(字符串) md5校验值,用来校验此条数据返回是否真实有效
        """
        file = open(file_path, mode="rb")
        file_data = file.read()
        file_base64 = base64.b64encode(file_data)
        file.close()
        url = "http://upload.chaojiying.net/Upload/Processing.php"
        data = {
            'user': username,
            'pass': password,
            'softid': soft_id,
            'codetype': code_type,
            'len_min': len_min,
            'file_base64': file_base64
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        parseData = parse.urlencode(data).encode('utf8')
        req = request.Request(url, parseData, headers)
        response = request.urlopen(req)
        result = response.read().decode()
        return json.loads(result)

    def error_captcha(self, username: str, password: str, soft_id: str, pic_id: str) -> Optional[dict]:
        """
        识别报错返分

        :param username: 用户名
        :param password: 密码
        :param soft_id: 软件ID
        :param pic_id: 图片ID 对应 getCaptcha返回值的pic_id 字段
        :return: JSON
            err_no,(数值) 返回代码
            err_str,(字符串) 中文描述的返回信息
        """
        url = "http://upload.chaojiying.net/Upload/ReportError.php"
        data = {
            'user': username,
            'pass': password,
            'softid': soft_id,
            'id': pic_id,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        parseData = parse.urlencode(data).encode('utf8')
        req = request.Request(url, parseData, headers)
        response = request.urlopen(req)
        result = response.read().decode()
        return json.loads(result)

    def score_captcha(self, username: str, password: str) -> Optional[dict]:
        """
        查询验证码剩余题分

        :param username: 用户名
        :param password: 密码
        :return: JSON
            err_no,(数值) 返回代码
            err_str,(字符串) 中文描述的返回信息
            tifen,(数值) 题分
            tifen_lock,(数值) 锁定题分
        """
        url = "http://upload.chaojiying.net/Upload/GetScore.php"
        data = {
            'user': username,
            'pass': password,
        }
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:24.0) Gecko/20100101 Firefox/24.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        parseData = parse.urlencode(data).encode('utf8')
        req = request.Request(url, parseData, headers)
        response = request.urlopen(req)
        result = response.read().decode()
        return json.loads(result)

    # #############
    #   语音服务   #
    # #############
    def activate_speech_service(self, activate_key: str) -> bool:
        """
        激活 initSpeechService (不支持win7)

        :param activate_key: 激活密钥，联系管理员
        :return: True或者False
        """
        return self.__send_data("activateSpeechService", activate_key) == "true"

    def init_speech_service(self, speech_key: str, speech_region: str) -> bool:
        """
        初始化语音服务(不支持win7)，需要调用 activateSpeechService 激活

        :param speech_key: 密钥
        :param speech_region: 区域
        :return: True或者False
        """
        return self.__send_data("initSpeechService", speech_key, speech_region) == "true"

    def audio_file_to_text(self, file_path, language: str) -> Optional[str]:
        """
        音频文件转文本

        :param file_path: 音频文件路径
        :param language: 语言，参考开发文档 语言和发音人
        :return: 转换后的音频文本或者None
        """
        response = self.__send_data("audioFileToText", file_path, language)
        if response == "null":
            return None
        return response

    def microphone_to_text(self, language: str) -> Optional[str]:
        """
        麦克风输入流转换文本

        :param language: 语言，参考开发文档 语言和发音人
        :return: 转换后的音频文本或者None
        """
        response = self.__send_data("microphoneToText", language)
        if response == "null":
            return None
        return response

    def text_to_bullhorn(self, ssmlPath_or_text: str, language: str, voice_name: str) -> bool:
        """
        文本合成音频到扬声器

        :param ssmlPath_or_text: 要转换语音的文本或者".xml"格式文件路径
        :param language: 语言，参考开发文档 语言和发音人
        :param voice_name: 发音人，参考开发文档 语言和发音人
        :return: True或者False
        """
        return self.__send_data("textToBullhorn", ssmlPath_or_text, language, voice_name) == "true"

    def text_to_audio_file(self, ssmlPath_or_text: str, language: str, voice_name: str, audio_path: str) -> bool:
        """
        文本合成音频并保存到文件

        :param ssmlPath_or_text: 要转换语音的文本或者".xml"格式文件路径
        :param language: 语言，参考开发文档 语言和发音人
        :param voice_name: 发音人，参考开发文档 语言和发音人
        :param audio_path: 保存音频文件路径
        :return: True或者False
        """
        return self.__send_data("textToAudioFile", ssmlPath_or_text, language, voice_name, audio_path) == "true"

    def microphone_translation_text(self, source_language: str, target_language: str) -> Optional[str]:
        """
        麦克风输入流转换文本

        :param source_language: 要翻译的语言，参考开发文档 语言和发音人
        :param target_language: 翻译后的语言，参考开发文档 语言和发音人
        :return: 转换后的音频文本或者None
        """
        response = self.__send_data("microphoneTranslationText", source_language, target_language)
        if response == "null":
            return None
        return response

    def audio_file_translation_text(self, audio_path: str, source_language: str, target_language: str) -> Optional[str]:
        """
        麦克风输入流转换文本

        :param audio_path: 要翻译的音频文件路径
        :param source_language: 要翻译的语言，参考开发文档 语言和发音人
        :param target_language: 翻译后的语言，参考开发文档 语言和发音人
        :return: 转换后的音频文本或者None
        """
        response = self.__send_data("audioFileTranslationText", audio_path, source_language, target_language)
        if response == "null":
            return None
        return response

    # #############
    #    数字人   #
    # #############
    def init_metahuman(self, metahuman_mde_path: str, metahuman_scale_value: str,
                       is_update_metahuman: bool = False) -> bool:
        """
        初始化数字人，第一次初始化需要一些时间

        :param metahuman_mde_path: 数字人模型路径
        :param metahuman_scale_value: 数字人缩放倍数，1为原始大小。为0.5时放大一倍，2则缩小一半
        :param is_update_metahuman: 是否强制更新，默认fasle。为true时强制更新会拖慢初始化速度
        :return: True或者False
        """
        return self.__send_data("initMetahuman", metahuman_mde_path, metahuman_scale_value,
                                is_update_metahuman) == "true"

    def metahuman_speech(self, save_voice_folder: str, text: str, language: str, voice_name: str,
                         quality: int = 0, wait_play_sound: bool = True, speech_rate: int = 0,
                         voice_style: str = "General") -> bool:
        """
        数字人说话，此函数需要调用 initSpeechService 初始化语音服务

        :param save_voice_folder: 保存的发音文件目录，文件名以0开始依次增加，扩展为.wav格式
        :param text: 要转换语音的文本
        :param language: 语言，参考开发文档 语言和发音人
        :param voice_name: 发音人，参考开发文档 语言和发音人
        :param quality: 音质，0低品质  1中品质  2高品质， 默认为0低品质
        :param wait_play_sound: 等待音频播报完毕，默认为 true等待
        :param speech_rate:  语速，默认为0，取值范围 -100 至 200
        :param voice_style: 语音风格，默认General常规风格，其他风格参考开发文档 语言和发音人
        :return: True或者False
        """
        return self.__send_data("metahumanSpeech", save_voice_folder, text, language, voice_name, quality,
                                wait_play_sound, speech_rate, voice_style) == "true"

    def metahuman_speech_cache(self, save_voice_folder: str, text: str, language: str, voice_name: str,
                               quality: int = 0, wait_play_sound: bool = True, speech_rate: int = 0,
                               voice_style: str = "General") -> bool:
        """
        *数字人说话缓存模式，需要调用 initSpeechService 初始化语音服务。函数一般用于常用的话术播报，非常用话术切勿使用，否则内存泄漏

        :param save_voice_folder: 保存的发音文件目录，文件名以0开始依次增加，扩展为.wav格式
        :param text: 要转换语音的文本
        :param language: 语言，参考开发文档 语言和发音人
        :param voice_name: 发音人，参考开发文档 语言和发音人
        :param quality: 音质，0低品质  1中品质  2高品质， 默认为0低品质
        :param wait_play_sound: 等待音频播报完毕，默认为 true等待
        :param speech_rate:  语速，默认为0，取值范围 -100 至 200
        :param voice_style: 语音风格，默认General常规风格，其他风格参考开发文档 语言和发音人
        :return: True或者False
        """
        return self.__send_data("metahumanSpeechCache", save_voice_folder, text, language, voice_name, quality,
                                wait_play_sound, speech_rate, voice_style) == "true"

    def metahuman_insert_video(self, video_file_path: str, audio_file_path: str, wait_play_video: bool = True) -> bool:
        """
        数字人插入视频

        :param video_file_path: 插入的视频文件路径
        :param audio_file_path: 插入的音频文件路径
        :param wait_play_video: 等待视频播放完毕，默认为 true等待
        :return: True或者False
        """
        return self.__send_data("metahumanInsertVideo", video_file_path, audio_file_path, wait_play_video) == "true"

    def replace_background(self, bg_file_path: str, replace_red: int = -1, replace_green: int = -1,
                           replace_blue: int = -1, sim_value: int = 0) -> bool:
        """
        替换数字人背景

        :param bg_file_path: 数字人背景 图片/视频 路径，默认不替换背景。仅替换绿幕背景的数字人模型
        :param replace_red: 数字人背景的三通道之一的 R通道色值。默认-1 自动提取
        :param replace_green: 数字人背景的三通道之一的 G通道色值。默认-1 自动提取
        :param replace_blue: 数字人背景的三通道之一的 B通道色值。默认-1 自动提取
        :param sim_value: 相似度。 默认为0，取值应当大于等于0
        :return: True或者False
        """
        return self.__send_data("replaceBackground", bg_file_path, replace_red, replace_green, replace_blue,
                                sim_value) == "true"

    def show_speech_text(self, origin_y: int = 0, font_type: str = "Arial", font_size: int = 30, font_red: int = 128,
                         font_green: int = 255, font_blue: int = 0, italic: bool = False,
                         underline: bool = False) -> bool:
        """
        显示数字人说话的文本

        :param origin_y, 第一个字显示的起始Y坐标点。 默认0 自适应高度
        :param font_type, 字体样式，支持操作系统已安装的字体。例如"Arial"、"微软雅黑"、"楷体"
        :param font_size, 字体的大小。默认30
        :param font_red, 字体颜色三通道之一的 R通道色值。默认128
        :param font_green, 字体颜色三通道之一的 G通道色值。默认255
        :param font_blue, 字体颜色三通道之一的 B通道色值。默认0
        :param italic, 是否斜体,默认false
        :param underline, 是否有下划线,默认false
        :return: True或者False
        """
        return self.__send_data("showSpeechText", origin_y, font_type, font_size, font_red, font_green, font_blue,
                                italic, underline) == "true"

    def make_metahuman_video(self, save_video_folder: str, text: str, language: str, voice_name: str, bg_file_path: str,
                               sim_value: float = 0, voice_style: str = "General", quality: int = 0, speech_rate: int = 0,
                               ) -> bool:
        """
        生成数字人短视频，此函数需要调用 initSpeechService 初始化语音服务

        :param save_video_folder: 保存的视频目录
        :param text: 要转换语音的文本
        :param language: 语言，参考开发文档 语言和发音人
        :param voice_name: 发音人，参考开发文档 语言和发音人
        :param bg_file_path: 数字人背景 图片/视频 路径，扣除绿幕会自动获取绿幕的RGB值，null 则不替换背景。仅替换绿幕背景的数字人模型
        :param sim_value: 相似度，默认为0。此处参数用作绿幕扣除微调RBG值。取值应当大于等于0
        :param voice_style: 语音风格，默认General常规风格，其他风格参考开发文档 语言和发音人
        :param quality: 音质，0低品质  1中品质  2高品质， 默认为0低品质
        :param speech_rate:  语速，默认为0，取值范围 -100 至 200
        :return: True或者False
        """
        return self.__send_data("makeMetahumanVideo", save_video_folder, text, language, voice_name, bg_file_path, sim_value, voice_style, quality,
                                speech_rate) == "true"

    #################
    #   驱动程序相关   #
    #################
    def get_extend_param(self) -> Optional[str]:
        """
        获取WindowsDriver.exe 命令扩展参数

        :return: WindowsDriver 驱动程序的命令行["extendParam"] 字段的参数
        """
        return self.__send_data("getExtendParam")

    def close_driver(self) -> bool:
        """
        关闭WindowsDriver.exe驱动程序

        :return:
        """
        self.__send_data("closeDriver")
        return

    # #############
    #    Hid      #
    # #############
    def init_hid(self) -> bool:
        """
        初始化Hid

        :return: True或者False
        """
        return self.__send_data("initHid") == "true"
    
    def get_hid_data(self) -> List[str]:
        """
        获取Hid相关数据

        :return: 激活成功的hid手机的安卓ID
        """
        response = self.__send_data("getHidData")
        if response == "":
            return []
        return response.split("|")
    
    def hid_press(self, android_id: str, angle: float, x: float, y: float) -> bool:
        """
        按下

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :param x: 横坐标
        :param y: 纵坐标
        :return: True或者False
        """
        return self.__send_data("hidPress", android_id, angle, x, y) == "true"
    
    def hid_move(self, android_id: str, angle: float, x: float, y: float, duration: float) -> bool:
        """
        移动

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :param x: 横坐标
        :param y: 纵坐标
        :param duration: 移动时长,秒
        :return: True或者False
        """
        return self.__send_data("hidMove", android_id, angle, x, y, duration * 1000) == "true"
    
    def hid_release(self, android_id: str, angle: float) -> bool:
        """
        释放

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :return: True或者False
        """
        return self.__send_data("hidRelease", android_id, angle) == "true"
    
    def hid_click(self, android_id: str, angle: float, x: float, y: float) -> bool:
        """
        单击

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :param x: 横坐标
        :param y: 纵坐标
        :return: True或者False
        """
        return self.__send_data("hidClick", android_id, angle, x, y) == "true"
    
    def hid_double_click(self, android_id: str, angle: float, x: float, y: float) -> bool:
        """
        双击

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :param x: 横坐标
        :param y: 纵坐标
        :return: True或者False
        """
        return self.__send_data("hidDoubleClick", android_id, angle, x, y) == "true"
    
    def hid_long_click(self, android_id: str, angle: float, x: float, y: float, duration: float) -> bool:
        """
        长按

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :param x: 横坐标
        :param y: 纵坐标
        :param duration: 按下时长,秒
        :return: True或者False
        """
        return self.__send_data("hidLongClick", android_id, angle, x, y, duration * 1000) == "true"
    
    def hid_swipe(self, android_id: str, angle: float, startX: float, startY: float, endX: float, endY: float, duration: float) -> bool:
        """
        滑动坐标

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :param startX: 起始横坐标
        :param startY: 起始纵坐标
        :param endX: 结束横坐标
        :param endY: 结束纵坐标
        :param duration: 滑动时长,秒
        :return: True或者False
        """
        return self.__send_data("hidSwipe", android_id, angle, startX, startY, endX, endY, duration * 1000) == "true"
    
    def hid_gesture(self, android_id: str, angle: float, gesture_path: List[_Point_Tuple], duration: float) -> bool:
        """
        Hid手势

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :param gesture_path: 手势路径，由一系列坐标点组成
        :param duration: 手势执行时长, 单位秒
        :return:
        """

        gesture_path_str = ""
        for point in gesture_path:
            gesture_path_str += f"{point[0]}/{point[1]}/\n"
        gesture_path_str = gesture_path_str.strip()

        return self.__send_data("hidDispatchGesture", android_id, angle, gesture_path_str, duration * 1000) == "true"
    
    def hid_gestures(self, android_id: str, angle: float, gestures_path: List[List['duration': float, _Point_Tuple]]) -> bool:
        """
        Hid多个手势

        :param android_id: 安卓id
        :param angle: 手机旋转角度
        :param gestures_path: [[duration:number, [x:number, y:number], [x1:number, y1:number]...],[duration, [x1, y1], [x1, y1]...],...]duration:手势执行时长, 单位秒,gesture_path手势路径，由一系列坐标点组成
        :return:
        """

        gestures_path_str = ""
        for gesture_path in gestures_path:
            gestures_path_str += f"{gesture_path[0] * 1000}/"
            for point in gesture_path[1:len(gesture_path)]:
                gestures_path_str += f"{point[0]}/{point[1]}/\n"
            gestures_path_str += "\r\n"
        gestures_path_str = gestures_path_str.strip()
        
        return self.__send_data("hidDispatchGestures", android_id, angle, gestures_path_str) == "true"

    # ##########
    #   其他   #
    ############
    def handle(self) -> None:
        # 设置阻塞模式
        # self.request.setblocking(False)

        # 设置缓冲区
        # self.request.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65535)
        self.request.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 1024 * 1024)  # 发送缓冲区 10M

        # 执行脚本
        self.script_main()

    @abc.abstractmethod
    def script_main(self):
        """脚本入口，由子类重写
        """

    @classmethod
    def execute(cls, listen_port: int, local: bool = True):
        """
        多线程启动 Socket 服务

        :param listen_port: 脚本监听的端口
        :param local: 脚本是否部署在本地
        :return:
        """

        if listen_port < 0 or listen_port > 65535:
            raise OSError("`listen_port` must be in 0-65535.")
        print("启动服务...")
        # 获取 IPv4 可用地址
        address_info = socket.getaddrinfo(None, listen_port, socket.AF_INET, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[
            0]
        *_, socket_address = address_info

        # 如果是本地部署，则自动启动 WindowsDriver.exe
        if local:
            try:
                print("尝试本地启动 WindowsDriver ...")
                subprocess.Popen(["WindowsDriver.exe", "127.0.0.1", str(listen_port)])
                print("本地启动 WindowsDriver 成功，开始执行脚本")
            except FileNotFoundError as e:
                err_msg = "\n异常排除步骤：\n1. 检查 Aibote.exe 路径是否存在中文；\n2. 是否启动 Aibote.exe 初始化环境变量；\n3. 检查电脑环境变量是否初始化成功，环境变量中是否存在 %Aibote% 开头的；\n4. 首次初始化环境变量后，是否重启开发工具；\n5. 是否以管理员权限启动开发工具；\n"
                print("\033[92m", err_msg, "\033[0m")
                raise e
        else:
            print("等待驱动连接...")

        # 启动 Socket 服务
        sock = _ThreadingTCPServer(socket_address, cls, bind_and_activate=True)
        sock.serve_forever()
