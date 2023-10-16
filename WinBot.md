# #############
#   窗口操作   #
# #############
def find_window(class_name: str = None, window_name: str = None) -> Optional[str]:
    """
    查找窗口句柄，仅查找顶级窗口，不包含子窗口
    :param class_name: 窗口类名
    :param window_name: 窗口名
    :return:
    """


def find_windows(class_name: str = None, window_name: str = None) -> List[str]:
    """
    查找窗口句柄数组，仅查找顶级窗口，不包含子窗口
    class_name 和 window_name 都为 None，则返回所有窗口句柄
    :param class_name: 窗口类名
    :param window_name: 窗口名
    :return:
    """


def find_sub_window(hwnd: str, class_name: str = None, window_name: str = None) -> Optional[str]:
    """
    查找子窗口句柄
    :param hwnd: 当前窗口句柄
    :param class_name: 窗口类名
    :param window_name: 窗口名
    :return:
    """


def find_parent_window(hwnd: str) -> Optional[str]:
    """
    查找父窗口句柄
    :param hwnd: 当前窗口句柄
    :return:
    """


def get_window_name(hwnd: str) -> Optional[str]:
    """
    获取窗口名称
    :param hwnd: 当前窗口句柄
    :return:
    """


def show_window(hwnd: str, show: bool) -> bool:
    """
    显示/隐藏窗口
    :param hwnd: 当前窗口句柄
    :param show: 是否显示窗口
    :return:
    """


def set_window_top(hwnd: str, top: bool = True) -> bool:
    """
    设置窗口到最顶层
    :param hwnd: 当前窗口句柄
    :param top: 是否置顶，True 置顶， False 取消置顶
    :return:
    """


# #############
#   键鼠操作   #
# #############
def move_mouse(hwnd: str, x: float, y: float, mode: bool = False, ele_hwnd: str = "0") -> bool:
    """
    移动鼠标
    :param hwnd: 当前窗口句柄
    :param x: 横坐标
    :param y: 纵坐标
    :param mode: 操作模式，后台 true，前台 false, 默认前台操作
    :param ele_hwnd: 元素句柄，如果 mode=True 且目标控件有单独的句柄，则需要通过 get_element_window 获得元素句柄，指定 ele_hwnd 的值(极少应用窗口由父窗口响应消息，则无需指定);
    :return:
    """


def scroll_mouse(hwnd: str, x: float, y: float, count: int, mode: bool = False) -> bool:
    """
    滚动鼠标
    :param hwnd: 当前窗口句柄
    :param x: 横坐标
    :param y: 纵坐标
    :param count: 鼠标滚动次数, 负数下滚鼠标, 正数上滚鼠标
    :param mode: 操作模式，后台 true，前台 false, 默认前台操作
    :return:
    """


def click_mouse(hwnd: str, x: float, y: float, typ: int, mode: bool = False, ele_hwnd: str = "0") -> bool:
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


def send_keys(text: str) -> bool:
    """
    输入文本
    :param text: 输入的文本
    :return:
    """


def send_keys_by_hwnd(hwnd: str, text: str) -> bool:
    """
    后台输入文本(杀毒软件可能会拦截)
    :param hwnd: 窗口句柄
    :param text: 输入的文本
    :return:
    """


def send_vk(vk: int, typ: int) -> bool:
    """
    输入虚拟键值(VK)
    :param vk: VK键值
    :param typ: 输入类型，按下弹起:1 按下:2 弹起:3
    :return:
    """


def send_vk_by_hwnd(hwnd: str, vk: int, typ: int) -> bool:
    """
    后台输入虚拟键值(VK)
    :param hwnd: 窗口句柄
    :param vk: VK键值
    :param typ: 输入类型，按下弹起:1 按下:2 弹起:3
    :return:
    """


# #############
#   图色操作   #
# #############
def save_screenshot(hwnd: str, save_path: str, region: _Region = None, algorithm: _Algorithm = None, mode: bool = False) -> bool:
    """
    截图
    :param hwnd: 窗口句柄；
    :param save_path: 图片存储路径；
    :param region: 截图区域，默认全屏；
    :param algorithm: 处理截图所用算法和参数，默认保存原图；
    :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
    :return:

    # 区域相关参数
    region = (0, 0, 0, 0) 按元素顺序分别代表：起点x、起点y、终点x、终点y，最终得到一个矩形。
    # 算法相关参数
    algorithm = (0, 0, 0) # 按元素顺序分别代表：algorithm_type 算法类型、threshold 阈值、max_val 最大值。
    threshold 和 max_val 同为 255 时灰度处理.
    0   THRESH_BINARY      算法，当前点值大于阈值 threshold 时，取最大值 max_val，否则设置为 0；
    1   THRESH_BINARY_INV  算法，当前点值大于阈值 threshold 时，设置为 0，否则设置为最大值 max_val；
    2   THRESH_TOZERO      算法，当前点值大于阈值 threshold 时，不改变，否则设置为 0；
    3   THRESH_TOZERO_INV  算法，当前点值大于阈值 threshold 时，设置为 0，否则不改变；
    4   THRESH_TRUNC       算法，当前点值大于阈值 threshold 时，设置为阈值 threshold，否则不改变；
    5   ADAPTIVE_THRESH_MEAN_C      算法，自适应阈值；
    6   ADAPTIVE_THRESH_GAUSSIAN_C  算法，自适应阈值；
    """


def get_color(hwnd: str, x: float, y: float, mode: bool = False) -> Optional[str]:
    """
    获取指定坐标点的色值，返回色值字符串(#008577)或者 None
    :param hwnd: 窗口句柄；
    :param x: x 坐标；
    :param y: y 坐标；
    :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
    :return:
    """


def find_color(hwnd: str, color: str, sub_colors: _SubColors = None, region: _Region = None,
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
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:

    # 区域相关参数
    region = (0, 0, 0, 0) 按元素顺序分别代表：起点x、起点y、终点x、终点y，最终得到一个矩形。
    # 算法相关参数
    algorithm = (0, 0, 0) # 按元素顺序分别代表：algorithm_type 算法类型、threshold 阈值、max_val 最大值。
    threshold 和 max_val 同为 255 时灰度处理.
    0   THRESH_BINARY      算法，当前点值大于阈值 threshold 时，取最大值 max_val，否则设置为 0；
    1   THRESH_BINARY_INV  算法，当前点值大于阈值 threshold 时，设置为 0，否则设置为最大值 max_val；
    2   THRESH_TOZERO      算法，当前点值大于阈值 threshold 时，不改变，否则设置为 0；
    3   THRESH_TOZERO_INV  算法，当前点值大于阈值 threshold 时，设置为 0，否则不改变；
    4   THRESH_TRUNC       算法，当前点值大于阈值 threshold 时，设置为阈值 threshold，否则不改变；
    5   ADAPTIVE_THRESH_MEAN_C      算法，自适应阈值；
    6   ADAPTIVE_THRESH_GAUSSIAN_C  算法，自适应阈值；
    """


def find_images(hwnd: str, image_path: str, region: _Region = None, algorithm: _Algorithm = None,
                similarity: float = 0.9, mode: bool = False, multi: int = 1, wait_time: float = None,
                interval_time: float = None) -> List[_Point]:
    """
    寻找图片坐标，在当前屏幕中寻找给定图片中心点的坐标，返回坐标列表
    :param hwnd: 窗口句柄；
    :param image_path: 图片的绝对路径；
    :param region: 从指定区域中找图，默认全屏；
    :param algorithm: 处理屏幕截图所用的算法，默认原图，注意：给定图片处理时所用的算法，应该和此方法的算法一致；
    :param similarity: 相似度，0-1 的浮点数，默认 0.9；
    :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
    :param multi: 返回图片数量，默认1张；
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:

    # 区域相关参数
    region = (0, 0, 0, 0) 按元素顺序分别代表：起点x、起点y、终点x、终点y，最终得到一个矩形。
    # 算法相关参数
    algorithm = (0, 0, 0) # 按元素顺序分别代表：algorithm_type 算法类型、threshold 阈值、max_val 最大值。
    threshold 和 max_val 同为 255 时灰度处理.
    0   THRESH_BINARY      算法，当前点值大于阈值 threshold 时，取最大值 max_val，否则设置为 0；
    1   THRESH_BINARY_INV  算法，当前点值大于阈值 threshold 时，设置为 0，否则设置为最大值 max_val；
    2   THRESH_TOZERO      算法，当前点值大于阈值 threshold 时，不改变，否则设置为 0；
    3   THRESH_TOZERO_INV  算法，当前点值大于阈值 threshold 时，设置为 0，否则不改变；
    4   THRESH_TRUNC       算法，当前点值大于阈值 threshold 时，设置为阈值 threshold，否则不改变；
    5   ADAPTIVE_THRESH_MEAN_C      算法，自适应阈值；
    6   ADAPTIVE_THRESH_GAUSSIAN_C  算法，自适应阈值；
    """


def find_dynamic_image(hwnd: str, interval_ti: int, region: _Region = None, mode: bool = False,
                       wait_time: float = None, interval_time: float = None) -> List[_Point]:
    """
    找动态图，对比同一张图在不同时刻是否发生变化，返回坐标列表
    :param hwnd: 窗口句柄；
    :param interval_ti: 前后时刻的间隔时间，单位毫秒；
    :param region: 在指定区域找图，默认全屏；
    :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


# ##############
#   OCR 相关   #
# ##############
def get_text(hwnd_or_image_path: str, region: _Region = None, mode: bool = False) -> List[str]:
    """
    通过 OCR 识别窗口/图片中的文字，返回文字列表
    :param hwnd_or_image_path: 窗口句柄或者图片路径；
    :param region: 识别区域，默认全屏；
    :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
    :return:
    """


def find_text(hwnd_or_image_path: str, text: str, region: _Region = None, mode: bool = False) -> List[_Point]:
    """
    通过 OCR 识别窗口/图片中的文字，返回文字列表
    :param hwnd_or_image_path: 识别区域，默认全屏；
    :param text: 要查找的文字；
    :param region: 识别区域，默认全屏；
    :param mode: 操作模式，后台 true，前台 false, 默认前台操作；
    :return:
    """


# ##############
#   元素操作   #
# ##############

def get_element_name(hwnd: str, xpath: str, wait_time: float = None, interval_time: float = None) -> Optional[str]:
    """
    获取元素名称
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


def get_element_value(hwnd: str, xpath: str, wait_time: float = None, interval_time: float = None) -> Optional[str]:
    """
    获取元素文本
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


def get_element_rect(hwnd: str, xpath: str, wait_time: float = None, interval_time: float = None) -> Optional[Tuple[_Point, _Point]]:
    """
    获取元素矩形，返回左上和右下坐标
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


def get_element_window(hwnd: str, xpath: str, wait_time: float = None, interval_time: float = None) -> Optional[str]:
    """
    获取元素窗口句柄
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


def click_element(hwnd: str, xpath: str, typ: int, wait_time: float = None,
                  interval_time: float = None) -> bool:
    """
    获取元素窗口句柄
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param typ: 操作类型，单击左键:1 单击右键:2 按下左键:3 弹起左键:4 按下右键:5 弹起右键:6 双击左键:7 双击右键:8
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


def set_element_focus(hwnd: str, xpath: str, wait_time: float = None,
                      interval_time: float = None) -> bool:
    """
    设置元素作为焦点
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


def set_element_value(hwnd: str, xpath: str, value: str,
                      wait_time: float = None, interval_time: float = None) -> bool:
    """
    设置元素文本
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param value: 要设置的内容
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


def scroll_element(hwnd: str, xpath: str, horizontal: int, vertical: int,
                   wait_time: float = None, interval_time: float = None) -> bool:
    """
    滚动元素
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param horizontal: 水平百分比 -1不滚动
    :param vertical: 垂直百分比 -1不滚动
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :return:
    """


def close_window(hwnd: str, xpath: str) -> bool:
    """
    关闭窗口
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :return:
    """


def set_element_state(hwnd: str, xpath: str, state: str) -> bool:
    """
    设置窗口状态
    :param hwnd: 窗口句柄
    :param xpath: 元素路径
    :param state: 0正常 1最大化 2 最小化
    :return:
    """


# ###############
#   系统剪切板   #
# ###############
def set_clipboard_text(text: str) -> bool:
    """
    设置剪切板内容
    :param text: 要设置的内容
    :return:
    """


def get_clipboard_text() -> str:
    """
    设置剪切板内容
    :return:
    """


# #############
#   启动进程   #
# #############

def start_process(cmd: str, show_window=True, is_wait=False) -> bool:
    """
    执行cmd命令
    :param cmd: 命令
    :param show_window: 是否显示窗口，默认显示
    :param is_wait: 是否等待程序结束， 默认不等待
    :return:
    """


def download_file(url: str, file_path: str, is_wait: bool) -> bool:
    """
    下载文件
    :param url: 文件地址
    :param file_path: 文件保存的路径
    :param is_wait: 是否等待下载完成
    :return:
    """
