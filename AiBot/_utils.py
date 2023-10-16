import abc
from typing import Union, Tuple, List


class Point:

    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def get_points_center(self, other_point: "Point") -> "Point":
        """
        获取两个坐标点的中间坐标

        :param other_point: 其他的坐标点
        :return:
        """
        return self.__class__(x=self.x + (other_point.x - self.x) / 2, y=self.y + (other_point.y - self.y) / 2)

    def __getitem__(self, item: int):
        if item == 0:
            return self.x
        elif item == 1:
            return self.y
        else:
            raise IndexError("list index out of range")

    def __repr__(self):
        return f"Point(x={self.x}, y={self.y})"


_Point_Tuple = Union[Point, Tuple[float, float]]
_Region = Tuple[float, float, float, float]
_Algorithm = Tuple[int, int, int]
_SubColors = List[Tuple[int, int, str]]


def _protect(*protected):
    """
    元类工厂，禁止类属性或方法被子类重写

    :param protected: 禁止重写的属性或方法
    :return:
    """

    class Protect(abc.ABCMeta):
        # 是否父类
        is_parent_class = True

        def __new__(mcs, name, bases, namespace):
            # 不是父类，需要检查属性是否被重写
            if not mcs.is_parent_class:
                attr_names = namespace.keys()
                for attr in protected:
                    if attr in attr_names:
                        raise AttributeError(f'Overriding of attribute `{attr}` not allowed.')
            # 首次调用后设置为 False
            mcs.is_parent_class = False
            return super().__new__(mcs, name, bases, namespace)

    return Protect
