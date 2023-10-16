#############
# 页面和导航 #
#############
def goto(url: str) -> bool:
    """
    跳转页面
    :param url:
    :return:
    """


def new_page(url: str) -> bool:
    """
    新建 Tab 并跳转页面
    :param url:
    :return:
    """


def back() -> bool:
    """
    后退
    :return:
    """


def forward() -> bool:
    """
    前进
    :return:
    """


def refresh() -> bool:
    """
    刷新
    :return:
    """


def save_screenshot(xpath: str = None) -> Optional[str]:
    """
    截图，返回 PNG 格式的 base64
    :param xpath: 元素路径，如果指定该参数则截取元素图片；
    :return:
    """


def get_current_page_id() -> Optional[str]:
    """
    获取当前页面 ID
    :return:
    """


def get_all_page_id() -> list:
    """
    获取所有页面 ID
    :return:
    """


def switch_to_page(page_id: str) -> bool:
    """
    切换到指定页面
    :param page_id:
    :return:
    """


def close_current_page() -> bool:
    """
    关闭当前页面
    :return:
    """


def get_current_url() -> Optional[str]:
    """
    获取当前页面 URL
    :return:
    """


def get_current_title() -> Optional[str]:
    """
    获取当前页面标题
    :return:
    """


###############
# iframe 操作 #
###############

def switch_to_frame(xpath) -> bool:
    """
    切换到指定 frame
    :param xpath:
    :return:
    """


def switch_to_main_frame() -> bool:
    """
    切回主 frame
    :return:
    """


###########
# 元素操作 #
###########
def click_element(xpath: str) -> bool:
    """
    点击元素
    :param xpath:
    :return:
    """


def get_element_text(xpath: str) -> Optional[str]:
    """
    获取元素文本
    :param xpath:
    :return:
    """


def get_element_rect(xpath: str) -> Optional[Tuple[_Point, _Point]]:
    """
    获取元素矩形坐标
    :param xpath:
    :return:
    """


def get_element_attr(xpath: str, attr_name: str) -> Optional[str]:
    """
    获取元素的属性
    :param xpath:
    :param attr_name:
    :return:
    """


def get_element_outer_html(xpath: str) -> Optional[str]:
    """
    获取元素的 outerHtml
    :param xpath:
    :return:
    """


def get_element_inner_html(xpath: str) -> Optional[str]:
    """
    获取元素的 innerHtml
    :param xpath:
    :return:
    """


def is_selected(xpath: str) -> bool:
    """
    元素是否已选中
    :param xpath:
    :return:
    """


def is_displayed(xpath: str) -> bool:
    """
    元素是否可见
    :param xpath:
    :return:
    """


def is_available(xpath: str) -> bool:
    """
    元素是否可用
    :param xpath:
    :return:
    """


def clear_element(xpath: str) -> bool:
    """
    清除元素值
    :param xpath:
    :return:
    """


def set_element_focus(xpath: str) -> bool:
    """
    设置元素焦点
    :param xpath:
    :return:
    """


def upload_file_by_element(xpath: str, file_path: str) -> bool:
    """
    通过元素上传文件
    :param xpath:
    :param file_path:
    :return:
    """


def send_keys(xpath: str, value: str) -> bool:
    """
    输入值
    :param xpath:
    :param value:
    :return:
    """


def set_element_value(xpath: str, value: str) -> bool:
    """
    设置元素值
    :param xpath:
    :param value:
    :return:
    """


def set_element_attr(xpath: str, attr_name: str, attr_value: str) -> bool:
    """
    设置元素属性
    :param xpath:
    :param attr_name:
    :param attr_value:
    :return:
    """


def send_vk(vk: str) -> bool:
    """
    输入值
    :param vk:
    :return:
    """


###########
# 键鼠操作 #
###########
def click_mouse(point: _Point_Tuple) -> bool:
    """
    点击鼠标
    :param point: 坐标点
    :return:
    """


def move_mouse(point: _Point_Tuple) -> bool:
    """
    移动鼠标
    :param point: 坐标点
    :return:
    """


def scroll_mouse(start_p: _Point_Tuple, end_p: _Point_Tuple) -> bool:
    """
    滚动鼠标
    :param start_p: 开始坐标点
    :param end_p: 结束坐标点
    :return:
    """


def click_mouse_by_element(xpath: str) -> bool:
    """
    根据元素位置点击鼠标
    :param xpath:
    :return:
    """


def move_to_element(xpath: str) -> bool:
    """
    移动鼠标到元素位置
    :param xpath:
    :return:
    """


def scroll_to_element(xpath: str) -> bool:
    """
    滚动鼠标到元素位置
    :param xpath:
    :return:
    """


#############
#   Alert   #
#############
def click_alert(accept: bool, prompt_text: str) -> bool:
    """
    点击警告框
    :param accept: 确认或取消
    :param prompt_text: 警告框文本
    :return:
    """


def get_alert_text() -> Optional[str]:
    """
    获取警告框文本
    :return:
    """


###############
#   窗口操作   #
###############
def get_window_pos() -> Optional[dict]:
    """
    获取窗口位置、尺寸和状态；
    返回窗口左上角坐标点，宽度和高度，状态
    :return:
    """


###############
#   Cookies   #
###############

def get_cookies(url: str) -> Optional[list]:
    """
    获取指定 url 的 Cookies
    :param url:
    :return:
    """


def get_all_cookies() -> Optional[list]:
    """
    获取所有的 Cookies
    :return:
    """


def set_cookies(url: str, name: str, value: str, options: dict = None) -> bool:
    """
    设置指定 url 的 Cookies
    :param url: 要设置 Cookie 的域
    :param name: Cookie 名
    :param value: Cookie 值
    :param options: 其他属性
    :return:
    """


def delete_cookies(name: str, url: str = "", domain: str = "", path: str = "") -> bool:
    """
    删除指定 Cookie
    :param name: 要删除的 Cookie 的名称
    :param url: 删除所有匹配 url 和 name 的 Cookie
    :param domain: 删除所有匹配 domain 和 name 的 Cookie
    :param path: 删除所有匹配 path 和 name 的 Cookie
    :return:
    """


def delete_all_cookies() -> bool:
    """
    删除所有 Cookie
    :return:
    """


def clear_cache() -> bool:
    """
    清除缓存
    :return:
    """


##############
#   JS 注入   #
##############
def execute_script(script: str) -> Optional[Any]:
    """
    注入执行 JS
    :param script: 要执行的 JS 代码
    :return: 假如注入代码有返回值，则返回此值，否则返回 None;

    result = execute_script('(()=>"aibote rpa")()')
    print(result)  # "aibote rpa"
    """
