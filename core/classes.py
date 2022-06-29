"""
various classes used in the program

Author:
Nilusink
"""
import typing as tp
import numpy as np


class Vec2:
    x: float
    y: float
    angle: float
    length: float

    def __init__(self) -> None:
        self.__x: float = 0
        self.__y: float = 0
        self.__angle: float = 0
        self.__length: float = 0

    # variable getters / setters
    @property
    def x(self):
        return self.__x

    @x.setter
    def x(self, value):
        self.__x = value
        self.__update("c")

    @property
    def y(self):
        return self.__y

    @y.setter
    def y(self, value):
        self.__y = value
        self.__update("c")

    @property
    def xy(self):
        return self.__x, self.__y

    @xy.setter
    def xy(self, xy):
        self.__x = xy[0]
        self.__y = xy[1]
        self.__update("c")

    @property
    def angle(self):
        """
        value in radian
        """
        return self.__angle

    @angle.setter
    def angle(self, value):
        """
        value in radian
        """
        value = self.normalize_angle(value)

        self.__angle = value
        self.__update("p")

    @property
    def length(self):
        return self.__length

    @length.setter
    def length(self, value):
        self.__length = value
        self.__update("p")

    @property
    def polar(self):
        return self.__angle, self.__length

    @polar.setter
    def polar(self, polar):
        self.__angle = polar[0]
        self.__length = polar[1]
        self.__update("p")

    # interaction
    def split_vector(self, direction):
        """
        :param direction: A vector facing in the wanted direction
        :return: tuple[Vector in only that direction, everything else]
        """
        a = (direction.angle - self.angle)
        facing = Vec2.from_polar(angle=direction.angle, length=self.length * np.cos(a))
        other = Vec2.from_polar(angle=direction.angle - np.pi / 2, length=self.length * np.sin(a))

        return facing, other

    def copy(self):
        return Vec2().from_cartesian(x=self.x, y=self.y)

    def to_dict(self) -> dict:
        return {
            "x": self.x,
            "y": self.y,
            "angle": self.angle,
            "length": self.length,
        }

    def normalize(self) -> "Vec2":
        self.length = 1
        return self

    def mirror(self, mirror_by: "Vec2") -> "Vec2":
        print(f"mirroring by {mirror_by}")
        mirror_by = mirror_by.copy().normalize()

        ang_d = mirror_by.angle - self.angle
        self.angle = mirror_by.angle + 2 * ang_d

        return self

    def reflect(self, reflect_by: "Vec2") -> "Vec2":
        t1, t2 = self.split_vector(reflect_by)
        self.xy = (t1 - t2).xy
        return self

    # maths
    def __add__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x + other.x, y=self.y + other.y)

        return Vec2.from_cartesian(x=self.x + other, y=self.y + other)

    def __sub__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x - other.x, y=self.y - other.y)

        return Vec2.from_cartesian(x=self.x - other, y=self.y - other)

    def __mul__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_polar(angle=self.angle + other.angle, length=self.length * other.length)

        return Vec2.from_polar(angle=self.angle, length=self.length * other)

    def __truediv__(self, other):
        if issubclass(type(other), Vec2):
            return Vec2.from_cartesian(x=self.x / other, y=self.y / other)

        return Vec2.from_polar(angle=self.angle, length=self.length / other)

    # internal functions
    def __update(self, calc_from):
        """
        :param calc_from: polar (p) | cartesian (c)
        """
        if calc_from in ("p", "polar"):
            self.__x = np.cos(self.angle) * self.length
            self.__y = np.sin(self.angle) * self.length

        elif calc_from in ("c", "cartesian"):
            self.__length = np.sqrt(self.x**2 + self.y**2)
            if not self.x == self.y == 0:
                self.__angle = np.arctan2(self.y, self.x)

        else:
            raise ValueError("Invalid value for \"calc_from\"")

    def __abs__(self):
        return np.sqrt(self.x**2 + self.y**2)

    def __repr__(self):
        return f"<\n" \
               f"\tVec2:\n" \
               f"\tx:{self.x}\ty:{self.y}\n" \
               f"\tangle:{self.angle}\tlength:{self.length}\n" \
               f">"

    # static methods.
    # creation of new instances
    @staticmethod
    def from_cartesian(x, y) -> "Vec2":
        p = Vec2()
        p.xy = x, y

        return p

    @staticmethod
    def from_polar(angle, length) -> "Vec2":
        p = Vec2()
        p.polar = angle, length

        return p

    @staticmethod
    def from_dict(dictionary: dict) -> "Vec2":
        if "x" in dictionary and "y" in dictionary:
            return Vec2.from_cartesian(x=dictionary["x"], y=dictionary["y"])

        elif "angle" in dictionary and "length" in dictionary:
            return Vec2.from_polar(angle=dictionary["angle"], length=dictionary["length"])

        else:
            raise KeyError("either (x & y) or (angle & length) must be in dict!")

    @staticmethod
    def normalize_angle(value: float) -> float:
        while value > 2 * np.pi:
            value -= 2 * np.pi

        while value < -2 * np.pi:
            value += 2 * np.pi

        return value