import abc
import json
import multiprocessing
import os
import socket
import socketserver
import sys
import threading
import time
from AiBot import WinBotMain
from ast import literal_eval
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Union

from loguru import logger

# from ._multiprocess import multiprocess

from ._utils import _protect, _Region, _Algorithm, _SubColors

spawn = multiprocessing.get_context("spawn")

# _LOG_PATH = Path(__file__).parent.resolve() / "logs"

# # rotation 文件分割，可按时间或者大小分割
# # retention 日志保留时间
# # compression="zip" 压缩方式
#
# # logger.add(LOG_PATH / 'runtime.log', rotation='100 MB', retention='15 days')  按大小分割，日志保留 15 天
# # logger.add(LOG_PATH / 'runtime.log', rotation='1 week')  # rotation 按时间分割，每周分割一次
#
# # 按时间分割，每日 12:00 分割一次，保留 15 天
# logger.add(_LOG_PATH / "runtime_{time}.log", rotation="12:00", retention="15 days")

# 高级方法
# debug_fo = logger.add("debug.log", filter=lambda record: record["level"].name == "DEBUG")
# debug_logger = logger.bind(name=debug_fo)

# logger.add("a.log", filter=lambda record: record["extra"].get("name") == "a")
# logger.add("b.log", filter=lambda record: record["extra"].get("name") == "b")
# logger_a = logger.bind(name="a")
# logger_b = logger.bind(name="b")

Log_Format = "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | " \
             "<level>{level: <8}</level> | " \
             "{process.id} - {thread.id: <8} | " \
             "<cyan>{module}:{line}</cyan> | " \
             "<level>{message}</level>"  # 日志内容


class Point:
    def __init__(self, x: float, y: float, driver: "AndroidBotMain"):
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


class Point2s:
    """
    代替 Point 元组
    """

    def __init__(self, p1: Point, p2: Point):
        self.p1 = p1
        self.p2 = p2

    def click(self, offset_x: float = 0, offset_y: float = 0) -> bool:
        """
        点击元素的中心坐标

        :param offset_x:
        :param offset_y:
        :return:
        """
        return self.central_point().click(offset_x=offset_x, offset_y=offset_y)

    def central_point(self) -> Point:
        """
        获取元素的中心坐标

        :return:
        """
        return self.p1.get_points_center(self.p2)

    def __getitem__(self, item):
        if item == 0:
            return self.p1
        elif item == 1:
            return self.p2
        else:
            raise IndexError("list index out of range")

    def __repr__(self):
        return f"({self.p1}, {self.p2})"


_Point_Tuple = Union[Point, Tuple[float, float]]

_AndroidId = ''
_AndroidIds = ''
_WindowsBot = ''
class CustomWinScript(WinBotMain):
    log_level = "DEBUG"

    def script_main(self):
        _WindowsBot = self

class _ThreadingTCPServer(socketserver.ThreadingTCPServer):
    daemon_threads = True
    allow_reuse_address = True

    def server_bind(self) -> None:
        """Called by constructor to bind the socket.
        May be overridden.
        """
        if os.name != "nt":
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1)
        else:  # In windows, SO_REUSEPORT is not available
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.bind(self.server_address)
        self.server_address = self.socket.getsockname()


Count = 0


class AndroidBotMain(socketserver.BaseRequestHandler, metaclass=_protect("handle", "execute")):
    raise_err = False
    wait_timeout = 3  # seconds
    interval_timeout = 0.5  # seconds

    log_storage = False
    log_level = "INFO"
    log_size = 10  # MB

    # 基础存储路径
    _base_path = "/storage/emulated/0/Android/data/com.aibot.client/files/"

    def __init__(self, request, client_address, server):
        self._lock = threading.Lock()
        self.log = logger

        if self.log_storage:
            global Count
            Count += 1
            thread_id = threading.current_thread().ident
            log_path = f"./logs/runtime{Count}_{thread_id}.log"
            self.log.add(log_path, level=self.log_level.upper(), format=Log_Format,
                         filter=lambda record: record['thread'].id == thread_id,
                         rotation=f'{self.log_size} MB',
                         retention='0 days')

        super().__init__(request, client_address, server)

    def __send_data_return_bytes(self, *args) -> bytes:
        args_len = ""
        args_text = ""

        for argv in args:
            argv = str(argv)
            args_text += argv
            args_len += str(len(bytes(argv, 'utf8'))) + "/"

        data = (args_len.strip("/") + "\n" + args_text).encode("utf8")
        try:
            with self._lock:
                self.log.debug(rf"---> {data}")
                self.request.sendall(data)
                response = self.request.recv(65535)
                if response == b"":
                    raise ConnectionAbortedError(f"{self.client_address[0]}:{self.client_address[1]} 客户端断开链接")
                data_length, data = response.split(b"/", 1)
                while int(data_length) > len(data):
                    data += self.request.recv(65535)
                self.log.debug(rf"<--- {data}")
        except Exception as e:
            self.log.error("send/read tcp data error: " + str(e))
            raise e
        return data

    def __send_data(self, *args) -> str:
        data = self.__send_data_return_bytes(*args)
        return data.decode("utf8").strip()

    def __push_file(self, func_name: str, to_path: str, file: bytes):
        func_name = bytes(func_name, "utf8")
        to_path = bytes(to_path, "utf8")

        str_data = ""
        str_data += str(len(func_name)) + "/"  # func_name 字节长度
        str_data += str(len(to_path)) + "/"  # to_path 字节长度
        str_data += str(len(file)) + "\n"  # file 字节长度

        bytes_data = bytes(str_data, "utf8")
        bytes_data += func_name
        bytes_data += to_path
        bytes_data += file

        with self._lock:
            self.log.debug(rf"---> {bytes_data}")
            self.request.sendall(bytes_data)
            response = self.request.recv(65535)
            if response == b"":
                raise ConnectionAbortedError(f"{self.client_address[0]}:{self.client_address[1]} 客户端断开链接")
            data_length, data = response.split(b"/", 1)
            while int(data_length) > len(data):
                data += self.request.recv(65535)
            self.log.debug(rf"<--- {data}")

        return data.decode("utf8").strip()

    def __pull_file(self, *args) -> bytes:
        args_len = ""
        args_text = ""

        for argv in args:
            argv = str(argv)
            args_text += argv
            args_len += str(len(bytes(argv, 'utf8'))) + "/"

        data = (args_len.strip("/") + "\n" + args_text).encode("utf8")

        with self._lock:
            self.log.debug(rf"---> {data}")
            self.request.sendall(data)
            response = self.request.recv(65535)
            if response == b"":
                raise ConnectionAbortedError(f"{self.client_address[0]}:{self.client_address[1]} 客户端断开链接")
            data_length, data = response.split(b"/", 1)
            while int(data_length) > len(data):
                data += self.request.recv(65535)
            self.log.debug(rf"<--- {data}")

        return data

    def save_screenshot(self, image_name: str, region: _Region = None, algorithm: _Algorithm = None) -> Optional[str]:
        """
        保存截图，返回图片地址(手机中)或者 None

        :param image_name: 图片名称，保存在手机 /storage/emulated/0/Android/data/com.aibot.client/files/ 路径下；
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

        :return: 图片地址(手机中)或者 None

        """
        if image_name.find("/") != -1:
            raise ValueError("`image_name` cannot contain `/`.")

        if not region:
            region = [0, 0, 0, 0]

        if not algorithm:
            algorithm_type, threshold, max_val = [0, 0, 0]
        else:
            algorithm_type, threshold, max_val = algorithm
            if algorithm_type in (5, 6):
                threshold = 127
                max_val = 255

        response = self.__send_data("saveScreenshot", self._base_path + image_name, *region,
                                    algorithm_type, threshold, max_val)
        if response == "true":
            return self._base_path + image_name
        return None

    def save_element_screenshot(self, image_name: str, xpath: str) -> Optional[str]:
        """
        保存元素截图

        :param image_name: 图片名称，保存在手机 /storage/emulated/0/Android/data/com.aibot.client/files/ 路径下
        :param xpath: xpath路径
        :return: 图片地址(手机中)或者 None

        """
        rect = self.get_element_rect(xpath)
        if rect is None:
            return None
        return self.save_screenshot(image_name, region=(rect[0].x, rect[0].y, rect[1].x, rect[1].y))

    def take_screenshot(self, region: _Region = None, algorithm: _Algorithm = None, scale: float = 1.0) -> Optional[bytes]:
        """
        保存截图，返回图像字节格式或者"null"的字节格式

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
        :param algorithm:
            scale浮点型 图片缩放率, 默认为 1.0 原大小。小于1.0缩小，大于1.0放大

        :return: 图像字节格式或者"null"的字节格式

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

        response = self.__send_data_return_bytes("takeScreenshot", *region, algorithm_type, threshold, max_val, scale)
        if response == b'null':
            return None
        return response

    # #############
    #   色值相关   #
    # #############
    def get_color(self, point: _Point_Tuple) -> Optional[str]:
        """
        获取指定坐标点的色值

        :param point: 坐标点
        :return: 色值字符串(例如: #008577)或者 None

        """
        response = self.__send_data("getColor", point[0], point[1])
        if response == "null":
            return None
        return response

    def find_color(self,
                   color: str,
                   sub_colors: _SubColors = None,
                   region: _Region = None,
                   similarity: float = 0.9,
                   wait_time: float = None,
                   interval_time: float = None,
                   raise_err: bool = None) -> Optional[Point]:
        """
        获取指定色值的坐标点，返回坐标或者 None

        :param color: 颜色字符串，必须以 # 开头，例如：#008577；
        :param sub_colors: 辅助定位的其他颜色；
        :param region: 截图区域，默认全屏，``region = (起点x、起点y、终点x、终点y)``，得到一个矩形
        :param similarity: 相似度，0-1 的浮点数，默认 0.9；
        :param wait_time: 等待时间，默认取 self.wait_timeout；
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout；
        :param raise_err: 超时是否抛出异常；
        :return: 坐标或者 None

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
            response = self.__send_data("findColor", color, sub_colors_str, *region, similarity)
            # 找色失败
            if response == "-1.0|-1.0":
                time.sleep(interval_time)
            else:
                # 找色成功
                x, y = response.split("|")
                return Point(x=float(x), y=float(y), driver=self)
        # 超时
        if raise_err:
            raise TimeoutError("`find_color` 操作超时")
        return None

    def compare_color(self,
                   main_x: float,
                   main_y: float,
                   color: str,
                   sub_colors: _SubColors = None,
                   region: _Region = None,
                   similarity: float = 0.9,
                   wait_time: float = None,
                   interval_time: float = None,
                   raise_err: bool = None) -> bool:
        """
        比较指定坐标点的颜色值

        :param main_x: 主颜色所在的X坐标；
        :param main_y: 主颜色所在的Y坐标；
        :param color: 颜色字符串，必须以 # 开头，例如：#008577；
        :param sub_colors: 辅助定位的其他颜色；
        :param region: 截图区域，默认全屏，``region = (起点x、起点y、终点x、终点y)``，得到一个矩形
        :param similarity: 相似度，0-1 的浮点数，默认 0.9；
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
            return self.__send_data("compareColor", main_x, main_y, color, sub_colors_str, *region, similarity) == "true"
        # 超时
        if raise_err:
            raise TimeoutError("`compare_color` 操作超时")
        return None

    # #############
    #   找图相关   #
    # #############
    def find_image(self,
                   image_name, region: _Region = None,
                   algorithm: _Algorithm = None,
                   similarity: float = 0.9,
                   wait_time: float = None,
                   interval_time: float = None,
                   raise_err: bool = None) -> Optional[Point]:
        """
        寻找图片坐标，在当前屏幕中寻找给定图片中心点的坐标，返回图片坐标或者 None

        :param image_name: 图片名称（手机中）；
        :param region: 截图区域，默认全屏，``region = (起点x、起点y、终点x、终点y)``，得到一个矩形
        :param algorithm:
            处理屏幕截图所用的算法，默认原图，注意：给定图片处理时所用的算法，应该和此方法的算法一致；

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

        :param similarity: 相似度，0-1 的浮点数，默认 0.9
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常
        :return: 图片坐标或者 None

        """
        result = self.find_images(image_name, region, algorithm, similarity, 1, wait_time, interval_time, raise_err)
        if not result:
            return None
        return result[0]

    def find_images(self,
                    image_name,
                    region: _Region = None,
                    algorithm: _Algorithm = None,
                    similarity: float = 0.9,
                    multi: int = 1,
                    wait_time: float = None,
                    interval_time: float = None,
                    raise_err: bool = None) -> List[Point]:
        """
        寻找图片坐标，在当前屏幕中寻找给定图片中心点的坐标，返回坐标列表

        :param image_name: 图片名称（手机中）；
        :param region: 截图区域，默认全屏，``region = (起点x、起点y、终点x、终点y)``，得到一个矩形
        :param algorithm:
            处理屏幕截图所用的算法，默认原图，注意：给定图片处理时所用的算法，应该和此方法的算法一致；

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
        :param similarity: 相似度，0-1 的浮点数，默认 0.9；
        :param multi: 目标数量，默认为 1，找到 1 个目标后立即结束；
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常；
        :return:

        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

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
            response = self.__send_data("findImage", self._base_path + image_name, *region, similarity,
                                        algorithm_type, threshold, max_val, multi)
            # 找图失败
            if response == "-1.0|-1.0":
                time.sleep(interval_time)
            else:
                # 找图成功，返回图片左上角坐标
                # 分割出多个图片的坐标
                image_points = response.split("/")
                point_list = []
                for point_str in image_points:
                    x, y = point_str.split("|")
                    point_list.append(Point(x=float(x), y=float(y), driver=self))
                return point_list
        # 超时
        if raise_err:
            raise TimeoutError("`find_images` 操作超时")
        return []

    def find_dynamic_image(self,
                           interval_ti: int,
                           region: _Region = None,
                           wait_time: float = None,
                           interval_time: float = None,
                           raise_err: bool = None) -> List[Point]:
        """
        找动态图，对比同一张图在不同时刻是否发生变化，返回坐标列表

        :param interval_ti: 前后时刻的间隔时间，单位毫秒；
        :param region: 截图区域，默认全屏，``region = (起点x、起点y、终点x、终点y)``，得到一个矩形
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常；
        :return: 坐标列表

        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

        if not region:
            region = [0, 0, 0, 0]

        end_time = time.time() + wait_time
        while time.time() < end_time:
            response = self.__send_data("findAnimation", interval_ti, *region)
            # 找图失败
            if response == "-1.0|-1.0":
                time.sleep(interval_time)
            else:
                # 找图成功，返回图片左上角坐标
                # 分割出多个图片的坐标
                image_points = response.split("/")
                point_list = []
                for point_str in image_points:
                    x, y = point_str.split("|")
                    point_list.append(Point(x=float(x), y=float(y), driver=self))
                return point_list
        # 超时
        if raise_err:
            raise TimeoutError("`find_dynamic_image` 操作超时")
        return []

    # ################
    #   坐标操作相关   #
    # ################
    def click(self, point: _Point_Tuple, offset_x: float = 0, offset_y: float = 0) -> bool:
        """
        点击坐标

        :param point: 坐标
        :param offset_x: 坐标 x 轴偏移量
        :param offset_y: 坐标 y 轴偏移量
        :return:
        """
        return self.__send_data("click", point[0] + offset_x, point[1] + offset_y) == "true"

    def double_click(self, point: _Point_Tuple, offset_x: float = 0, offset_y: float = 0) -> bool:
        """
        双击坐标

        :param point: 坐标
        :param offset_x: 坐标 x 轴偏移量
        :param offset_y: 坐标 y 轴偏移量
        :return:
        """
        return self.__send_data("doubleClick", point[0] + offset_x, point[1] + offset_y) == "true"

    def long_click(self, point: _Point_Tuple, duration: float, offset_x: float = 0, offset_y: float = 0) -> bool:
        """
        长按坐标

        :param point: 坐标
        :param duration: 按住时长，单位秒
        :param offset_x: 坐标 x 轴偏移量
        :param offset_y: 坐标 y 轴偏移量
        :return:
        """
        return self.__send_data("longClick", point[0] + offset_x, point[1] + offset_y, duration * 1000) == "true"

    def swipe(self, start_point: _Point_Tuple, end_point: _Point_Tuple, duration: float) -> bool:
        """
        滑动坐标

        :param start_point: 起始坐标
        :param end_point: 结束坐标
        :param duration: 滑动时长，单位秒
        :return:
        """
        return self.__send_data("swipe", start_point[0], start_point[1], end_point[0], end_point[1],
                                duration * 1000) == "true"

    def gesture(self, gesture_path: List[_Point_Tuple], duration: float) -> bool:
        """
        执行手势

        :param gesture_path: 手势路径，由一系列坐标点组成
        :param duration: 手势执行时长, 单位秒
        :return:
        """

        gesture_path_str = ""
        for point in gesture_path:
            gesture_path_str += f"{point[0]}/{point[1]}/\n"
        gesture_path_str = gesture_path_str.strip()

        return self.__send_data("dispatchGesture", gesture_path_str, duration * 1000) == "true"

    def gestures(self, gestures_path: List[List['duration': float, _Point_Tuple]]) -> bool:
        """
        执行多个手势

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
        
        return self.__send_data("dispatchGestures", gestures_path_str) == "true"

    def press(self, point: _Point_Tuple, duration: float) -> bool:
        """
        手指按下

        :param point: 坐标
        :param duration: 持续时间，单位秒
        :return:
        """
        return self.__send_data("press", point[0], point[1], duration * 1000) == "true"

    def move(self, point: _Point_Tuple, duration: float) -> bool:
        """
        手指移动

        :param point: 坐标
        :param duration: 持续时间
        :return:
        """
        return self.__send_data("move", point[0], point[1], duration * 1000) == "true"

    def release(self) -> bool:
        """手指抬起"""
        return self.__send_data("release") == "true"

    def press_release(self, point: _Point_Tuple, duration: float) -> bool:
        """
        按下屏幕坐标点并释放

        :param point: 按压坐标
        :param duration: 按压时长，单位秒
        :return:
        """
        result = self.press(point, duration)
        if not result:
            return False
        time.sleep(duration)
        result2 = self.release()
        if not result2:
            return False
        return True

    def press_release_by_ele(self, xpath, duration: float, wait_time: float = None,
                             interval_time: float = None, ) -> bool:
        """
        按压元素并释放

        :param xpath: 要按压的元素
        :param duration: 按压时长，单位秒
        :param wait_time: 查找元素的最长等待时间
        :param interval_time: 查找元素的轮询间隔时间
        :return:
        """
        point2s = self.get_element_rect(xpath, wait_time=wait_time, interval_time=interval_time, raise_err=False)
        if point2s is None:
            return False
        return self.press_release(point2s.central_point(), duration)

    # ##############
    #   OCR 相关   #
    ################
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
        #
        # return text_info_list

        return literal_eval(text)

    def __ocr_server(self, region: _Region = None, algorithm: _Algorithm = None, scale: float = 1.0) -> list:
        """
        OCR 服务，通过 OCR 识别屏幕中文字

        :param region:
        :param algorithm:
        :param scale:
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

        # scale 仅支持区域识别
        if region[2] == 0:
            scale = 1.0

        response = self.__send_data("ocr", *region, algorithm_type, threshold, max_val, scale)
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

    def get_text(self, region: _Region = None, algorithm: _Algorithm = None, scale: float = 1.0) -> List[str]:
        """
        通过 OCR 识别屏幕中的文字，返回文字列表

        :param region: 识别区域，默认全屏；
        :param algorithm: 处理图片/屏幕所用算法和参数，默认保存原图；
        :param scale: 图片缩放率, 默认为 1.0 原大小。大于1.0放大，小于1.0缩小，不能为负数。仅在区域识别有效
        :return: 文字列表

        .. seealso::
            :meth:`find_image`: ``region`` 和 ``algorithm`` 的参数说明
        """
        text_info_list = self.__ocr_server(region, algorithm, scale)
        text_list = []
        for text_info in text_info_list:
            text = text_info[-1][0]
            text_list.append(text)
        return text_list

    def find_text(self, text: str, region: _Region = None, algorithm: _Algorithm = None, scale: float = 1.0) -> \
            List[Point]:
        """
        查找文字所在的坐标，返回坐标列表（坐标是文本区域中心位置）

        :param text: 要查找的文字；
        :param region: 识别区域，默认全屏；
        :param algorithm: 处理图片/屏幕所用算法和参数，默认保存原图；
        :param scale: 图片缩放率, 默认为 1.0 原大小。大于1.0放大，小于1.0缩小，不能为负数。仅在区域识别有效
        :return: 坐标列表（坐标是文本区域中心位置）

        .. seealso::
            :meth:`find_image`: ``region`` 和 ``algorithm`` 的参数说明
        """
        if not region:
            region = [0, 0, 0, 0]

        text_info_list = self.__ocr_server(region, algorithm, scale)

        text_points = []
        for text_info in text_info_list:
            if text in text_info[-1][0]:
                points, words_tuple = text_info

                left, top, right, bottom = points

                # 文本区域起点坐标
                start_x = left[0]
                start_y = left[1]
                # 文本区域终点坐标
                end_x = right[0]
                end_y = right[1]
                # 文本区域中心点据左上角的偏移量
                # 可能指定文本只是部分文本，要计算出实际位置(x轴)
                words: str = words_tuple[0]
                width = end_x - start_x

                # 单字符宽度
                single_word_width = width / len(words)
                # 文本在整体文本的起始位置
                pos = words.find(text)

                offset_x = pos * single_word_width + len(text) * single_word_width / 2
                offset_y = (end_y - start_y) / 2

                # [ { x: 108, y: 1153 } ]

                # 计算文本区域中心坐标
                text_point = Point(
                    x=float(region[0] + (start_x + offset_x) / scale),
                    y=float(region[1] + (start_y + offset_y) / scale),
                    driver=self
                )
                text_points.append(text_point)

        return text_points

    # #############
    #   元素操作   #
    ###############
    def get_element_rect(self, xpath: str, wait_time: float = None, interval_time: float = None,
                         raise_err: bool = None) -> Optional[Point2s]:
        """
        获取元素位置，返回元素区域左上角和右下角坐标

        :param xpath: xpath 路径
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常；
        :return: 元素区域左上角和右下角坐标
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

        end_time = time.time() + wait_time
        while time.time() < end_time:
            data = self.__send_data("getElementRect", xpath)
            # 失败
            if data == "-1|-1|-1|-1":
                time.sleep(interval_time)
            # 成功
            else:
                start_x, start_y, end_x, end_y = data.split("|")
                return Point2s(p1=Point(x=float(start_x), y=float(start_y), driver=self),
                               p2=Point(x=float(end_x), y=float(end_y), driver=self))
        # 超时
        if raise_err:
            raise TimeoutError("`get_element_rect` 操作超时")
        return None

    def get_element_desc(self, xpath: str, wait_time: float = None, interval_time: float = None,
                         raise_err: bool = None) -> Optional[str]:
        """
        获取元素描述

        :param xpath: xpath 路径
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常；
        :return: 元素描述字符串
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

        end_time = time.time() + wait_time
        while time.time() < end_time:
            data = self.__send_data("getElementDescription", xpath)
            # 失败
            if data == "null":
                time.sleep(interval_time)
            # 成功
            else:
                return data
        # 超时
        if raise_err:
            raise TimeoutError("`get_element_desc` 操作超时")
        return None

    def get_element_text(self, xpath: str, wait_time: float = None, interval_time: float = None,
                         raise_err: bool = None) -> Optional[str]:
        """
        获取元素文本

        :param xpath: xpath 路径
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常；
        :return: 元素文本
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

        end_time = time.time() + wait_time
        while time.time() < end_time:
            data = self.__send_data("getElementText", xpath)
            # 失败
            if data == "null":
                time.sleep(interval_time)
            # 成功
            else:
                return data
        # 超时
        if raise_err:
            raise TimeoutError("`get_element_text` 操作超时")
        return None

    def set_element_text(self, xpath: str, text: str, wait_time: float = None, interval_time: float = None,
                         raise_err: bool = None) -> bool:
        """
        设置元素文本

        :param xpath:
        :param text:
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

        end_time = time.time() + wait_time
        while time.time() < end_time:
            # 失败
            if self.__send_data("setElementText", xpath, text) != "true":
                time.sleep(interval_time)
            # 成功
            else:
                return True
        # 超时
        if raise_err:
            raise TimeoutError("`set_element_text` 操作超时")
        return False

    def click_element(self, xpath: str, wait_time: float = None, interval_time: float = None,
                      raise_err: bool = None) -> bool:
        """
        点击元素

        :param xpath:
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

        end_time = time.time() + wait_time
        while time.time() < end_time:
            # 失败
            if self.__send_data("clickElement", xpath) != "true":
                time.sleep(interval_time)
            # 成功
            else:
                return True
        # 超时
        if raise_err:
            raise TimeoutError("`click_element` 操作超时")
        return False

    def click_any_elements(self, xpath_list: List[str], wait_time: float = None, interval_time: float = None,
                           raise_err: bool = None) -> bool:
        """
        遍历点击列表中的元素，直到任意一个元素返回 True

        :param xpath_list: xpath 列表
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :param raise_err: 超时是否抛出异常；
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        if raise_err is None:
            raise_err = self.raise_err

        end_time = time.time() + wait_time
        while time.time() < end_time:
            for xpath in xpath_list:
                result = self.click_element(xpath, wait_time=0.05, interval_time=0.01, raise_err=False)
                if result:
                    return True
            time.sleep(interval_time)

        if raise_err:
            raise TimeoutError("`click_any_elements` 操作超时")
        return False

    def scroll_element(self, xpath: str, direction: int = 0) -> bool:
        """
        滚动元素，0 向上滑动，1 向下滑动

        :param xpath: xpath 路径
        :param direction: 滚动方向，0 向上滑动，1 向下滑动
        :return:
        """
        return self.__send_data("scrollElement", xpath, direction) == "true"

    def element_not_exists(self, xpath: str, wait_time: float = None, interval_time: float = None) -> bool:
        """
        元素是否不存在

        :param xpath: xpath 路径
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            # 存在
            if self.__send_data("existsElement", xpath) == "true":
                time.sleep(interval_time)
            # 不存在
            else:
                return True
        return False

    def element_exists(self, xpath: str, wait_time: float = None, interval_time: float = None) -> bool:
        """
        元素是否存在

        :param xpath: xpath 路径
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            # 失败
            if self.__send_data("existsElement", xpath) != "true":
                time.sleep(interval_time)
            # 成功
            else:
                return True
        return False

    def any_elements_exists(self, xpath_list: List[str], wait_time: float = None, interval_time: float = None) -> \
            Optional[str]:
        """
        遍历列表中的元素，只要任意一个元素存在就返回 True

        :param xpath_list: xpath 列表
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :return: 任意一个元素存在就返回 True
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            for xpath in xpath_list:
                result = self.element_exists(xpath, wait_time=0.05, interval_time=0.01)
                if result:
                    return xpath
            time.sleep(interval_time)
        return None

    def element_is_selected(self, xpath: str) -> bool:
        """
        元素是否存在

        :param xpath: xpath 路径
        :return:
        """
        return self.__send_data("isSelectedElement", xpath) == "true"

    def click_element_by_slide(self, xpath, distance: int = 1000, duration: float = 0.5, direction: int = 1,
                               count: int = 999, end_flag_xpath: str = None, wait_time: float = 600,
                               interval_time: float = 0.5, raise_err: bool = None) -> bool:
        """
        滑动列表，查找并点击指定元素

        :param xpath: xpath路径
        :param distance: 滑动距离，默认 1000
        :param duration: 滑动时间，默认 0.5 秒
        :param direction: 滑动方向，默认为 1； 1=上滑，2=下滑
        :param count: 滑动次数
        :param end_flag_xpath: 结束标志 xpath，无标志不检测此标志
        :param wait_time: 等待时间，默认 10 分钟
        :param interval_time: 轮询间隔时间，默认 0.5 秒
        :param raise_err: 超时是否抛出异常；
        :return:
        """
        if raise_err is None:
            raise_err = self.raise_err

        if direction == 1:
            _end_point = (500, 300)
            _start_point = (500, _end_point[1] + distance)
        elif direction == 2:
            _start_point = (500, 300)
            _end_point = (500, _start_point[1] + distance)
        else:
            raise RuntimeError(f"未知方向：{direction}")

        end_time = time.time() + wait_time
        current_count = 0
        while time.time() < end_time and current_count < count:
            current_count += 1

            if self.click_element(xpath, wait_time=1, interval_time=0.5, raise_err=False):
                return True

            if end_flag_xpath and self.element_exists(end_flag_xpath, wait_time=1, interval_time=0.5):
                return False

            self.swipe(_start_point, _end_point, duration)
            time.sleep(interval_time)

        if raise_err:
            raise TimeoutError("`click_element_by_slide` 操作超时")
        return False

    # #############
    #   文件传输   #
    # #############
    def push_file(self, origin_path: str, to_path: str) -> bool:
        """
        将电脑文件传输到手机端

        :param origin_path: 源文件路径
        :param to_path: 目标存储路径
        :return:

        ex:
        origin_path: /
        to_path: /storage/emulated/0/Android/data/com.aibot.client/files/code479259.png
        """
        if not to_path.startswith("/storage/emulated/0/"):
            to_path = "/storage/emulated/0/" + to_path

        with open(origin_path, "rb") as file:
            data = file.read()

        return self.__push_file("pushFile", to_path, data) == "true"

    def pull_file(self, remote_path: str, local_path: str) -> bool:
        """
        将手机文件传输到电脑端

        :param remote_path: 手机端文件路径
        :param local_path: 电脑本地文件存储路径
        :return:

        ex:
        remote_path: /storage/emulated/0/Android/data/com.aibot.client/files/code479259.png
        local_path: /
        """
        if not remote_path.startswith("/storage/emulated/0/"):
            remote_path = "/storage/emulated/0/" + remote_path

        data = self.__pull_file("pullFile", remote_path)
        if data == b"null":
            return False

        with open(local_path, "wb") as file:
            file.write(data)
        return True

    # #############
    #   设备操作   #
    # #############

    def start_app(self, name: str, wait_time: float = None, interval_time: float = None) -> bool:
        """
        启动 APP

        :param name: APP名字或者包名
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            # 失败
            if self.__send_data("startApp", name) != "true":
                time.sleep(interval_time)
            # 成功
            else:
                return True
        # 超时
        return False

    def app_is_running(self, name: str, wait_time: float = None, interval_time: float = None) -> bool:
        """
        启动 APP

        :param name: APP名字或者包名
        :param wait_time: 等待时间，默认取 self.wait_timeout
        :param interval_time: 轮询间隔时间，默认取 self.interval_timeout
        :return:
        """
        if wait_time is None:
            wait_time = self.wait_timeout

        if interval_time is None:
            interval_time = self.interval_timeout

        end_time = time.time() + wait_time
        while time.time() < end_time:
            # 失败
            if self.__send_data("appIsRunnig", name) != "true":
                time.sleep(interval_time)
            # 成功
            else:
                return True
        # 超时
        return False
    
    def get_installed_packages(self) -> List[str]:
        """
        获取已安装app的包名(不包含系统APP)

        :return:
        """

        response = self.__send_data("getTnstalledPackages")
        if response == "null":
            return []
        return response.split("|")

    def get_device_ip(self) -> str:
        """
        获取设备IP地址

        :return: 设备IP地址字符串
        """
        return self.client_address[0]

    def get_android_id(self) -> str:
        """
        获取 Android 设备 ID
        :return: Android 设备 ID 字符串
        """
        return self.__send_data("getAndroidId")

    def get_group(self) -> str:
        """
        获取投屏组号
        :return: 投屏组号
        """
        return self.__send_data("getGroup")
    
    def get_identifier(self) -> str:
        """
        获取投屏编号
        :return: 投屏编号
        """
        return self.__send_data("getIdentifier")
    
    def get_title(self) -> str:
        """
        获取投屏标题
        :return: 投屏标题
        """
        return self.__send_data("getTitle")

    def get_window_size(self) -> Dict[str, float]:
        """
        获取屏幕大小

        :return: 屏幕大小, 字典格式
        """
        width, height = self.__send_data("getWindowSize").split("|")
        return {"width": float(width), "height": float(height)}

    def get_image_size(self, image_path) -> Dict[str, float]:
        """
        获取图片大小

        :param image_path: 图片路径
        :return: 图片大小, 字典格式
        """
        width, height = self.__send_data("getImageSize", image_path).split("|")
        return {"width": float(width), "height": float(height)}

    def show_toast(self, text: str, duration: float = 3) -> bool:
        """
        Toast 弹窗

        :param text: 弹窗内容
        :param duration: 弹窗持续时间，单位：秒
        :return:
        """
        return self.__send_data("showToast", text, duration * 1000) == "true"

    def sleep(self, wait_time: float, interval_time: float = 1.5):
        """
        强制等待

        :param wait_time: 等待时长
        :param interval_time: 等待时轮询间隔时间
        :return:
        """
        end_time = datetime.now().timestamp() + wait_time
        while datetime.now().timestamp() < end_time:
            self.show_toast("等待中...", 1)
            time.sleep(interval_time)

    def send_keys(self, text: str) -> bool:
        """
        发送文本，需要打开 AiBot 输入法

        :param text: 文本内容
        :return:
        """
        return self.__send_data("sendKeys", text) == "true"

    def send_vk(self, vk: int) -> bool:
        """
        发送 vk

        :param vk: 虚拟键值
        :return:

        虚拟键值按键对照表 https://blog.csdn.net/yaoyaozaiye/article/details/122826340
        """
        return self.__send_data("sendVk", vk) == "true"

    def write_android_file(self, remote_path: str, text: str, append: bool) -> bool:
        """
        写入安卓文件

        :param remote_path: 安卓文件路径
        :param text: 要写入的文本内容
        :param append: 是否追加模式
        :return:
        """
        if not remote_path.endswith(".txt"):
            raise TypeError("文件必须是.txt后缀结尾")

        if not remote_path.startswith("/storage/emulated/0/"):
            remote_path = "/storage/emulated/0/" + remote_path

        return self.__send_data("writeAndroidFile", remote_path, text, append) == "true"

    def read_android_file(self, remote_path: str) -> Optional[str]:
        """
        读取安卓文件

        :param remote_path: 安卓文件路径
        :return:
        """
        if not remote_path.startswith("/storage/emulated/0/"):
            remote_path = "/storage/emulated/0/" + remote_path

        response = self.__send_data("readAndroidFile", remote_path)
        if response == "null":
            return None
        return response

    def delete_android_file(self, remote_path: str) -> bool:
        """
        删除安卓文件

        :param remote_path: 安卓文件路径
        :return:
        """
        if not remote_path.startswith("/storage/emulated/0/"):
            remote_path = "/storage/emulated/0/" + remote_path

        return self.__send_data("deleteAndroidFile", remote_path) == "true"

    def exists_android_file(self, remote_path: str) -> bool:
        """
        安卓文件是否存在

        :param remote_path: 安卓文件路径
        :return:
        """
        if not remote_path.startswith("/storage/emulated/0/"):
            remote_path = "/storage/emulated/0/" + remote_path

        return self.__send_data("existsAndroidFile", remote_path) == "true"

    def get_android_sub_files(self, android_directory) -> List[str]:
        """
        获取文件夹内的所有文件(不包含深层子目录)

        :param android_directory: 安卓目录，安卓外部存储根目录 /storage/emulated/0/
        :return:
        """

        response = self.__send_data("getAndroidSubFiles", android_directory)
        if response == "null":
            return []
        return response.split("|")

    def back(self) -> bool:
        """
        返回

        :return:
        """
        return self.__send_data("back") == "true"

    def home(self) -> bool:
        """
        返回桌面

        :return:
        """
        return self.__send_data("home") == "true"

    def recent_tasks(self) -> bool:
        """
        显示最近任务

        :return:
        """
        return self.__send_data("recents") == "true"

    def open_uri(self, uri: str) -> bool:
        """
        唤起 app

        :param uri: app 唤醒协议
        :return:

        open_uri("alipayqr://platformapi/startapp?saId=10000007")
        """
        return self.__send_data("openUri", uri) == "true"

    def start_activity(self, action: str, uri: str = '', package_name: str = '', class_name: str = '',
                       typ: str = '') -> bool:
        """
        Intent 跳转

        :param action: 动作，例如 "android.intent.action.VIEW"
        :param uri: 跳转链接，例如：打开支付宝扫一扫界面，"alipayqr://platformapi/startapp?saId=10000007"
        :param package_name: 包名，"com.xxx.xxxxx"
        :param class_name: 类名
        :param typ: 类型
        :return: True或者 False
        """
        return self.__send_data("startActivity", action, uri, package_name, class_name, typ) == "true"

    def call_phone(self, mobile: str) -> bool:
        """
        拨打电话

        :param mobile: 手机号码
        :return:
        """
        return self.__send_data("callPhone", mobile) == "true"

    def send_msg(self, mobile, text) -> bool:
        """
        发送短信

        :param mobile: 手机号码
        :param text: 短信内容
        :return:
        """
        return self.__send_data("sendMsg", mobile, text) == "true"

    def get_activity(self) -> str:
        """
        获取活动页

        :return:
        """
        return self.__send_data("getActivity")

    def get_package(self) -> str:
        """
        获取包名

        :return:
        """
        return self.__send_data("getPackage")

    def set_clipboard_text(self, text: str) -> bool:
        """
        设置剪切板文本

        :param text:
        :return:
        """
        return self.__send_data("setClipboardText", text) == "true"

    def get_clipboard_text(self) -> str:
        """
        获取剪切板内容

        :return:
        """
        return self.__send_data("getClipboardText")

    # ##############
    #   控件与参数   #
    # ##############
    def create_text_view(self, _id: int, text: str, x: int, y: int, width: int = 400, height: int = 60):
        """
        创建文本框控件

        :param _id:  控件ID，不可与其他控件重复
        :param text:  控件文本
        :param x:  控件在屏幕上x坐标
        :param y:  控件在屏幕上y坐标
        :param width:  控件宽度，默认 400
        :param height:  控件高度，默认 60
        :return:
        """
        return self.__send_data("createTextView", _id, text, x, y, width, height)

    def create_edit_view(self, _id: int, text: str, x: int, y: int, width: int = 400, height: int = 150):
        """
        创建编辑框控件

        :param _id:  控件ID，不可与其他控件重复
        :param text:  控件文本
        :param x:  控件在屏幕上x坐标
        :param y:  控件在屏幕上y坐标
        :param width:  控件宽度，默认 400
        :param height:  控件高度，默认 150
        :return:
        """
        return self.__send_data("createEditText", _id, text, x, y, width, height)

    def create_check_box(self, _id: int, text: str, x: int, y: int, width: int = 400, height: int = 60):
        """
        创建复选框控件

        :param _id:  控件ID，不可与其他控件重复
        :param text:  控件文本
        :param x:  控件在屏幕上x坐标
        :param y:  控件在屏幕上y坐标
        :param width:  控件宽度，默认 400
        :param height:  控件高度，默认 60
        :return:
        """
        return self.__send_data("createCheckBox", _id, text, x, y, width, height)

    def create_web_view(self, _id: int, url: str, x: int = -1, y: int = -1, width: int = -1, height: int = -1) -> bool:
        """
        创建WebView控件

        :param _id: 控件ID，不可与其他控件重复
        :param url: 加载的链接
        :param x: 控件在屏幕上 x 坐标，值为 -1 时自动填充宽高
        :param y: 控件在屏幕上 y 坐标，值为 -1 时自动填充宽高
        :param width: 控件宽度，值为 -1 时自动填充宽高
        :param height: 控件高度，值为 -1 时自动填充宽高
        :return:
        """
        return self.__send_data("createWebView", _id, url, x, y, width, height) == "true"

    def clear_script_widget(self) -> bool:
        """
        清除脚本控件

        :return:
        """
        return self.__send_data("clearScriptControl") == "true"

    def get_script_params(self) -> Optional[dict]:
        """
        获取脚本参数

        :return:
        """
        response = self.__send_data("getScriptParam")
        if response == "null":
            return None
        try:
            params = json.loads(response)
        except Exception as e:
            self.show_toast(f"获取脚本参数异常: {e}")
            self.log.error(f"获取脚本参数异常: {e}")
            raise e
        return params

    def __start_windows_bot(self) -> None:

        CustomWinScript.execute(56668)

    def __init_accessory(self) -> bool:
        """
        初始化android Accessory，获取手机hid相关的数据。

        :return:
        """
        return self.__send_data("initAccessory") == "true"
    
    def init_hid(self) -> bool:
        """
        初始化Hid
        
        hid实际上是由windowsBot 通过数据线直接发送命令给安卓系统并执行，并不是由aibote.apk执行的命令。
        我们应当将所有设备准备就绪再调用此函数初始化。
        Windows initHid 和 android initAccessory函数 初始化目的是两者的数据交换，并告知windowsBot发送命令给哪台安卓设备

        :return:
        """
        # 启动windowsDriver,一次就行
        self.__start_windows_bot()
        tries = 5
        while tries > 0:
            if _WindowsBot:
                tries = 0
            else:
                tries = tries - 1
                time.sleep(1000)

        if not _WindowsBot:
            return False
        
        # 初始化android Accessory，获取手机hid相关的数据。 先调用 AndroidBot.windowsBot.initHid() 后再调用initAccessory() 顺序不能变
        if not self.__init_accessory():
            return False
        
        # 先调用 windowsBot.initHid，再调用androidBot.initHid。
        # 初始化完毕再通过windowsBot.getHidData获取交换后的hid相关的数据
        if not _WindowsBot.init_hid():
            return False
        
        if not _AndroidIds:
            _AndroidIds = _WindowsBot.get_hid_data()

        if not _AndroidIds:
            return False
        
        # 获取AndroidId 用作hid相关函数区分手机设备
        _AndroidId = self.get_android_id()
        for AndroidId in _AndroidIds:
            if AndroidId == _AndroidId:
                return True

        return False
    
    def get_rotation_angle(self) -> float:
        """
        获取手机旋转角度

        :return: 手机旋转的角度
        """
        return float(self.__send_data("getRotationAngle"))

    def hid_press(self, x: float, y: float) -> bool:
        """
        按下

        :param x: 横坐标
        :param y: 纵坐标
        :return: True或者False
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_press(_AndroidId, angle, x, y) == "true"

    def hid_move(self, x: float, y: float, duration: float) -> bool:
        """
        移动

        :param x: 横坐标
        :param y: 纵坐标
        :return: True或者False
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_move(_AndroidId, angle, x, y, duration * 1000) == "true"

    def hid_release(self) -> bool:
        """
        释放

        :return: True或者False
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_release(_AndroidId, angle) == "true"
    
    def hid_click(self, x: float, y: float) -> bool:
        """
        单击

        :param x: 横坐标
        :param y: 纵坐标
        :return: True或者False
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_click(_AndroidId, angle, x, y) == "true"
    
    def hid_double_click(self, x: float, y: float) -> bool:
        """
        双击

        :param x: 横坐标
        :param y: 纵坐标
        :return: True或者False
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_double_click(_AndroidId, angle, x, y) == "true"
    
    def hid_long_click(self, x: float, y: float, duration: float) -> bool:
        """
        长按

        :param x: 横坐标
        :param y: 纵坐标
        :param duration: 按下时长,秒
        :return: True或者False
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_long_click(_AndroidId, angle, x, y, duration * 1000) == "true"
    
    def hid_swipe(self, startX: float, startY: float, endX: float, endY: float, duration: float) -> bool:
        """
        滑动坐标

        :param startX: 起始横坐标
        :param startY: 起始纵坐标
        :param endX: 结束横坐标
        :param endY: 结束纵坐标
        :param duration: 滑动时长,秒
        :return: True或者False
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_swipe(_AndroidId, angle, startX, startY, endX, endY, duration * 1000) == "true"
    
    def hid_gesture(self, gesture_path: List[_Point_Tuple], duration: float) -> bool:
        """
        Hid手势

        :param gesture_path: 手势路径，由一系列坐标点组成
        :param duration: 手势执行时长, 单位秒
        :return:
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_gesture(_AndroidId, angle, gesture_path, duration * 1000) == "true"
    
    def hid_gestures(self, gestures_path: List[List['duration': float, _Point_Tuple]]) -> bool:
        """
        Hid多个手势

        :param gestures_path: [[duration:number, [x:number, y:number], [x1:number, y1:number]...],[duration, [x1, y1], [x1, y1]...],...]duration:手势执行时长, 单位秒,gesture_path手势路径，由一系列坐标点组成
        :return:
        """
        angle = self.get_rotation_angle()
        return _WindowsBot.hid_gestures(_AndroidId, angle, gestures_path) == "true"

    def close_driver(self) -> None:
        """
        关闭连接

        :return:
        """
        self.__send_data("closeDriver")
        return None
    
    # ##########
    #  URL请求 #
    ############
    def url_request(self, url: str, request_type: str, content_type: str = 'null', post_data: str = 'null') -> str:
        """
        发送URL请求

        :param url: 请求的地址，http:// 或者 https://开头
        :param request_type: 请求类型，GET或者POST
        :param content_type: 可选参数，用作POST 内容类型
        :param post_data: 可选参数，用作POST 提交的数据
        :return: 请求数据内容
        """
        return self.__send_data("urlRequest", url, request_type, content_type, post_data)

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
        :param code_type: 图片类型 参考 https://www.chaojiying.com/price.html
        :param len_min: 最小位数 默认0为不启用,图片类型为可变位长时可启用这个参数
        :return: JSON
            err_no,(数值) 返回代码  为0 表示正常，错误代码 参考 https://www.chaojiying.com/api-23.html
            err_str,(字符串) 中文描述的返回信息 
            pic_id,(字符串) 图片标识号，或图片id号
            pic_str,(字符串) 识别出的结果
            md5,(字符串) md5校验值,用来校验此条数据返回是否真实有效
        """
        if not file_path.startswith("/storage/emulated/0/"):
            file_path = "/storage/emulated/0/" + file_path

        response = self.__send_data("getCaptcha", file_path, username, password, soft_id, code_type, len_min)
        return json.loads(response)

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
        response = self.__send_data("errorCaptcha", username, password, soft_id, pic_id)
        return json.loads(response)

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
        response = self.__send_data("scoreCaptcha", username, password)
        return json.loads(response)

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
    def execute(cls, listen_port: int, multi: int = 1):
        """
        多线程启动 Socket 服务，执行脚本

        :return:
        """

        if listen_port < 0 or listen_port > 65535:
            raise OSError("`listen_port` must be in 0-65535.")

        if multi < 1:
            raise ValueError("`multi` must be >= 1.")

        # 获取 IPv4 可用地址
        address_info = \
            socket.getaddrinfo(None, listen_port, socket.AF_INET, socket.SOCK_STREAM, 0, socket.AI_PASSIVE)[0]
        *_, socket_address = address_info
        # 启动 Socket 服务
        sock = _ThreadingTCPServer(socket_address, cls, bind_and_activate=True)
        sock.request_queue_size = int(getattr(cls, "request_queue_size", 5))
        print(f"Server stared on {socket_address[0]}:{socket_address[1]}")
        print("服务已启动")
        print("等待设备连接...")

        sock.serve_forever()
