def save_screenshot(image_name: str, region: _Region = None, algorithm: _Algorithm = None) -> Optional[str]:
    """
    保存截图，返回图片地址(手机中)或者 None
    :param image_name: 图片名称，保存在手机 /storage/emulated/0/Android/data/com.aibot.client/files/ 路径下；
    :param region: 截图区域，默认全屏；
    :param algorithm: 处理截图所用算法和参数，默认保存原图；
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


def save_element_screenshot(image_name, xpath) -> Optional[str]:
    """
    保存元素截图，返回图片地址(手机中)或者 None
    :return:
    """


# #############
#   色值相关   #
# #############
def get_color(point: _Point_Tuple) -> Optional[str]:
    """
    获取指定坐标点的色值，返回色值字符串(#008577)或者 None
    :param point: 坐标点；
    :return:
    """


def find_color(color: str, sub_colors: _SubColors = None, region: _Region = None, similarity: float = 0.9,
               wait_time: float = None, interval_time: float = None, raise_err: bool = None) -> Optional[_Point]:
    """
    获取指定色值的坐标点，返回坐标或者 None
    :param color: 颜色字符串，必须以 # 开头，例如：#008577；
    :param sub_colors: 辅助定位的其他颜色；
    :param region: 在指定区域内找色，默认全屏；
    :param similarity: 相似度，0-1 的浮点数，默认 0.9；
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :param raise_err: 超时是否抛出异常；
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


# #############
#   找图相关   #
# #############
def find_image(image_name, region: _Region = None, algorithm: _Algorithm = None, similarity: float = 0.9,
               wait_time: float = None, interval_time: float = None, raise_err: bool = None) -> Optional[_Point]:
    """
    寻找图片坐标，在当前屏幕中寻找给定图片中心点的坐标，返回坐标或者 None
    :param image_name: 图片名称（手机中）；
    :param region: 从指定区域中找图，默认全屏；
    :param algorithm: 处理屏幕截图所用的算法，默认原图，注意：给定图片处理时所用的算法，应该和此方法的算法一致；
    :param similarity: 相似度，0-1 的浮点数，默认 0.9；
    :param wait_time: 等待时间，默认取 .wait_timeout；
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout；
    :param raise_err: 超时是否抛出异常；
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


def find_image_by_opencv(image_name, region: _Region = None, algorithm: _Algorithm = None,
                         similarity: float = 0.9, wait_time: float = None, interval_time: float = None,
                         raise_err: bool = None) -> Optional[_Point]:
    """
    寻找图片坐标，在当前屏幕中寻找给定图片中心点的坐标，返回图片坐标或者 None
    与 .find_image() 基本一致，采用 OpenCV 算法
    :param image_name: 图片名称（手机中）；
    :param region: 从指定区域中找图，默认全屏；
    :param algorithm: 处理屏幕截图所用的算法，默认原图，注意：给定图片处理时所用的算法，应该和此方法的算法一致；
    :param similarity: 相似度，0-1 的浮点数，默认 0.9；
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
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


def find_images_by_opencv(image_name, region: _Region = None, algorithm: _Algorithm = None,
                          similarity: float = 0.9, multi: int = 1, wait_time: float = None,
                          interval_time: float = None, raise_err: bool = None) -> List[_Point]:
    """
    寻找图片坐标，在当前屏幕中寻找给定图片中心点的坐标，返回坐标列表
    与 .find_image() 基本一致，采用 OpenCV 算法，并且可找多个目标。
    :param image_name: 图片名称（手机中）；
    :param region: 从指定区域中找图，默认全屏；
    :param algorithm: 处理屏幕截图所用的算法，默认原图，注意：给定图片处理时所用的算法，应该和此方法的算法一致；
    :param similarity: 相似度，0-1 的浮点数，默认 0.9；
    :param multi: 目标数量，默认为 1，找到 1 个目标后立即结束；
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
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


def find_dynamic_image(interval_ti: int, region: _Region = None, wait_time: float = None,
                       interval_time: float = None, raise_err: bool = None) -> List[_Point]:
    """
    找动态图，对比同一张图在不同时刻是否发生变化，返回坐标列表
    :param interval_ti: 前后时刻的间隔时间，单位毫秒；
    :param region: 在指定区域找图，默认全屏；
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:

    # 区域相关参数
    region = (0, 0, 0, 0) 按元素顺序分别代表：起点x、起点y、终点x、终点y，最终得到一个矩形。
    """


# ################
#   坐标操作相关   #
# ################
def click(point: _Point_Tuple, offset_x: float = 0, offset_y: float = 0) -> bool:
    """
    点击坐标
    :param point: 坐标；
    :param offset_x: 坐标 x 轴偏移量；
    :param offset_y: 坐标 y 轴偏移量；
    :return:
    """


def double_click(point: _Point_Tuple, offset_x: float = 0, offset_y: float = 0) -> bool:
    """
    双击坐标
    :param point: 坐标；
    :param offset_x: 坐标 x 轴偏移量；
    :param offset_y: 坐标 y 轴偏移量；
    :return:
    """


def long_click(point: _Point_Tuple, duration: float, offset_x: float = 0, offset_y: float = 0) -> bool:
    """
    长按坐标
    :param point: 坐标；
    :param duration: 按住时长，单位秒；
    :param offset_x: 坐标 x 轴偏移量；
    :param offset_y: 坐标 y 轴偏移量；
    :return:
    """


def swipe(start_point: _Point_Tuple, end_point: _Point_Tuple, duration: float) -> bool:
    """
    滑动坐标
    :param start_point: 起始坐标；
    :param end_point: 结束坐标；
    :param duration: 滑动时长，单位秒；
    :return:
    """


def gesture(gesture_path: List[_Point_Tuple], duration: float) -> bool:
    """
    执行手势
    :param gesture_path: 手势路径，由一系列坐标点组成
    :param duration: 手势执行时长, 单位秒
    :return:
    """


# ##############
#   OCR 相关   #
################


def get_text(region: _Region = None, scale: float = 1.0) -> List[str]:
    """
    通过 OCR 识别屏幕中的文字，返回文字列表
    :param region: 识别区域，默认全屏；
    :param scale: 图片缩放率，默认为 1.0，1.0 以下为缩小，1.0 以上为放大；
    :return:
    """


def find_text(text: str, region: _Region = None, scale: float = 1.0) -> List[_Point]:
    """
    查找文字所在的坐标，返回坐标列表（坐标是文本区域中心位置）
    :param text: 要查找的文字；
    :param region: 识别区域，默认全屏；
    :param scale: 图片缩放率，默认为 1.0，1.0 以下为缩小，1.0 以上为放大；
    :return:
    """


# #############
#   元素操作   #
###############
def get_element_rect(xpath: str, wait_time: float = None, interval_time: float = None,
                     raise_err: bool = None) -> Optional[Tuple[_Point, _Point]]:
    """
    获取元素位置，返回元素区域左上角和右下角坐标
    :param xpath: xpath 路径
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def get_element_desc(xpath: str, wait_time: float = None, interval_time: float = None,
                     raise_err: bool = None) -> Optional[str]:
    """
    获取元素描述
    :param xpath: xpath 路径
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def get_element_text(xpath: str, wait_time: float = None, interval_time: float = None,
                     raise_err: bool = None) -> Optional[str]:
    """
    获取元素文本
    :param xpath: xpath 路径
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def set_element_text(xpath: str, text: str, wait_time: float = None, interval_time: float = None,
                     raise_err: bool = None) -> bool:
    """
    设置元素文本
    :param xpath:
    :param text:
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def click_element(xpath: str, wait_time: float = None, interval_time: float = None,
                  raise_err: bool = None) -> bool:
    """
    点击元素
    :param xpath:
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def click_any_elements(xpath_list: List[str], wait_time: float = None, interval_time: float = None,
                       raise_err: bool = None) -> bool:
    """
    遍历点击列表中的元素，直到任意一个元素返回 True
    :param xpath_list: xpath 列表
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def scroll_element(xpath: str, direction: int = 0) -> bool:
    """
    滚动元素，0 向上滑动，1 向下滑动
    :param xpath: xpath 路径
    :param direction: 滚动方向，0 向上滑动，1 向下滑动
    :return:
    """


def element_not_exists(xpath: str, wait_time: float = None, interval_time: float = None,
                       raise_err: bool = None) -> bool:
    """
    元素是否不存在
    :param xpath: xpath 路径
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def element_exists(xpath: str, wait_time: float = None, interval_time: float = None,
                   raise_err: bool = None) -> bool:
    """
    元素是否存在
    :param xpath: xpath 路径
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def any_elements_exists(xpath_list: List[str], wait_time: float = None, interval_time: float = None,
                        raise_err: bool = None) -> Optional[str]:
    """
    遍历列表中的元素，只要任意一个元素存在就返回 True
    :param xpath_list: xpath 列表
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :param raise_err: 超时是否抛出异常；
    :return:
    """


def element_is_selected(xpath: str) -> bool:
    """
    元素是否存在
    :param xpath: xpath 路径
    :return:
    """


def click_element_by_slide(xpath, distance: int = 1000, duration: float = 0.5, direction: int = 1,
                           count: int = 999, end_flag_xpath: str = None, wait_time: float = 600,
                           interval_time: float = 0.5, raise_err: bool = None) -> bool:
    """
    滑动列表，查找并点击指定元素
    :param xpath:
    :param distance: 滑动距离，默认 1000
    :param duration: 滑动时间，默认 0.5 秒
    :param direction: 滑动方向，默认为 1； 1=上滑，2=下滑
    :param count: 滑动次数
    :param end_flag_xpath: 结束标志 xpath
    :param wait_time: 等待时间，默认 10 分钟
    :param interval_time: 轮询间隔时间，默认 0.5 秒
    :param raise_err: 超时是否抛出异常；
    :return:
    """


# #############
#   文件传输   #
# #############
def push_file(origin_path: str, to_path: str) -> bool:
    """
    将电脑文件传输到手机端
    :param origin_path: 源文件路径
    :param to_path: 目标存储路径
    :return:

    ex:
    origin_path: /
    to_path: /storage/emulated/0/Android/data/com.aibot.client/files/code479259.png
    """


def pull_file(remote_path: str, local_path: str) -> bool:
    """
    将手机文件传输到电脑端
    :param remote_path: 手机端文件路径
    :param local_path: 电脑本地文件存储路径
    :return:

    ex:
    remote_path: /storage/emulated/0/Android/data/com.aibot.client/files/code479259.png
    local_path: /
    """


# #############
#   设备操作   #
# #############

def start_app(name: str, wait_time: float = None, interval_time: float = None) -> bool:
    """
    启动 APP
    :param name: APP名字或者包名
    :param wait_time: 等待时间，默认取 .wait_timeout
    :param interval_time: 轮询间隔时间，默认取 .interval_timeout
    :return:
    """


def get_device_ip() -> str:
    """
    获取设备IP地址
    :return:
    """


def get_android_id() -> str:
    """
    获取 Android 设备 ID
    :return:
    """


def get_window_size() -> Dict[str, float]:
    """
    获取屏幕大小
    :return:
    """


def get_image_size(image_path) -> Dict[str, float]:
    """
    获取图片大小
    :param image_path: 图片路径；
    :return:
    """


def show_toast(text: str) -> bool:
    """
    Toast 弹窗
    :param text: 弹窗内容；
    :return:
    """


def send_keys(text: str) -> bool:
    """
    发送文本，需要打开 AiBot 输入法
    :param text: 文本内容
    :return:
    """


def send_vk(vk: int) -> bool:
    """
    发送文本，需要打开 AiBot 输入法
    :param vk: 虚拟键值
    :return:

    虚拟键值按键对照表 https://blog.csdn.net/yaoyaozaiye/article/details/122826340
    """


def back() -> bool:
    """
    返回
    :return:
    """


def home() -> bool:
    """
    返回桌面
    :return:
    """


def recent_tasks() -> bool:
    """
    显示最近任务
    :return:
    """


def open_uri(uri: str) -> bool:
    """
    唤起 app
    :param uri: app 唤醒协议
    :return:

    open_uri("alipayqr://platformapi/startapp?saId=10000007")
    """


def call_phone(mobile: str) -> bool:
    """
    拨打电话
    :param mobile: 手机号码
    :return:
    """


def send_msg(mobile, text) -> bool:
    """
    发送短信
    :param mobile: 手机号码
    :param text: 短信内容
    :return:
    """


def get_activity() -> str:
    """
    获取活动页
    :return:
    """


def get_package() -> str:
    """
    获取包名
    :return:
    """


def set_clipboard_text(text: str) -> bool:
    """
    设置剪切板文本
    :param text:
    :return:
    """


def get_clipboard_text() -> str:
    """
    获取剪切板内容
    :return:
    """


# ##############
#   控件与参数   #
# ##############
def create_text_view(_id: int, text: str, x: int, y: int, width: int = 400, height: int = 60):
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


def create_edit_view(_id: int, text: str, x: int, y: int, width: int = 400, height: int = 150):
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


def create_check_box(_id: int, text: str, x: int, y: int, width: int = 400, height: int = 60):
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


def get_script_params() -> Optional[dict]:
    """
    获取脚本参数
    :return:
    """
