from math import *

from kivy.graphics import Rectangle, Color, Ellipse, Line
from kivy.properties import NumericProperty, ColorProperty, StringProperty
from kivy.uix.button import Button
from kivy.uix.widget import Widget

from joystick.joystick import Joystick


class Pad(Joystick):
    def __init__(self, **kwargs):
        super(Pad, self).__init__(**kwargs)
        self.outer_size = 0.6
        self.inner_size = 0.6
        self.pad_size = 0.5


class ImageButton(Button):
    image_path = StringProperty()
    alpha = NumericProperty(1)
    image_color = ColorProperty()
    border_color = ColorProperty()
    border_width = NumericProperty(1)

    def on_release(self):
        self.alpha = 1


class FireBtn(ImageButton):
    pass


class Map:
    def __init__(self, parent: Widget):
        self.parent = parent
        self.pos = 0, 0
        self.size = 200, 100
        self.ship_radius = 3
        self.laser_radius = 1

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def x(self):
        return self.pos[0]

    @property
    def y(self):
        return self.pos[1]

    def get_radius(self, obj: str):
        if obj == "ship":
            return self.ship_radius
        elif obj == "laser":
            return self.laser_radius

    def convert_pos(self, pos, obj=None):
        x, y = self.convert_size(pos)
        if obj is not None:
            r = self.get_radius(obj)
        else:
            r = 0
        return x + self.x - r, y + self.y - r

    def convert_size(self, size):
        x = size[0] / self.parent.WIDTH * self.width
        y = size[1] / self.parent.HEIGHT * self.height
        return x, y

    def draw(self):
        from objects import Laser
        from player import Player
        from enemy import Enemy, UFO

        if self.parent is not None:
            self.pos = self.parent.width - self.width - self.ship_radius * 2 - 2, \
                       self.parent.height - self.height - self.ship_radius * 2 - 2
            border = Rectangle(pos=self.pos, size=self.size)
            self.parent.canvas.add(Color(1, 1, 1, 0.15))
            self.parent.canvas.add(border)

            for enemy in Enemy.Enemies:
                if not enemy.out_of_bounds():
                    if isinstance(enemy, Enemy):
                        c = Color(1, 0, 0, 1)
                    else:
                        c = Color(1, 160 / 255, 0, 1)
                    char = Ellipse(pos=self.convert_pos(enemy.curr_pos, "ship"),
                                   size=(self.ship_radius * 2, self.ship_radius * 2))
                    self.parent.canvas.add(c)
                    self.parent.canvas.add(char)

            for laser in Laser.Lasers:
                if not laser.out_of_bounds():
                    if laser.to == "enemy":
                        c = Color(1, 1, 1, 1)
                        l = Ellipse(pos=self.convert_pos(laser.curr_pos, "laser"),
                                    size=(self.laser_radius * 2, self.laser_radius * 2))
                        self.parent.canvas.add(c)
                        self.parent.canvas.add(l)

            if not self.parent.player.out_of_bounds():
                player = Ellipse(pos=self.convert_pos(self.parent.player.curr_pos, "ship"),
                                 size=(self.ship_radius * 2, self.ship_radius * 2))
                self.parent.canvas.add(Color(0, 0, 1))
                self.parent.canvas.add(player)

                foreground_shade = Rectangle(pos=self.convert_pos(self.parent.scroll),
                                             size=self.convert_size(self.parent.size))
                self.parent.canvas.add(Color(1, 1, 1, 0.3))
                self.parent.canvas.add(foreground_shade)


class Util:
    @staticmethod
    def is_mobile():
        from kivy.utils import platform
        return platform not in ['windows', 'macosx', 'linux']

    @staticmethod
    def size(widget: Widget, width_ratio, height_ratio):
        return widget.width * width_ratio, widget.height * height_ratio

    @staticmethod
    def distance_between_points(point1, point2):
        x = (point1[0] - point2[0]) ** 2
        y = (point1[1] - point2[1]) ** 2
        return (x + y) ** 0.5

    @staticmethod
    def angle_between_points(point1, point2, center):
        radius = Util.distance_between_points(point1, center)
        d = Util.distance_between_points(point1, point2)
        angle = 2 * asin(d / (2 * radius))
        return degrees(angle)

    @staticmethod
    def is_character(*sprites):
        from player import Player
        from enemy import Enemy, UFO
        for sprite in sprites:
            if not isinstance(sprite, (Player, Enemy, UFO)):
                return False
        return True

    @staticmethod
    def is_player(sprite):
        from player import Player
        return isinstance(sprite, Player)

    @staticmethod
    def is_enemy(*sprites):
        from enemy import Enemy, UFO
        for sprite in sprites:
            if not isinstance(sprite, (Enemy, UFO)):
                return False
        return True

    @staticmethod
    def two_point_line_inclination(point1, point2):
        dx = point2[0] - point1[0]
        dy = point2[1] - point1[1]
        angle = degrees(atan2(dy, dx))
        if angle < 0:
            return 360 + angle
        return angle

    @staticmethod
    def point_of_internal_division(point1, point2, m, n):
        x1, y1 = point1
        x2, y2 = point2
        x = (m * x2 + n * x1) / (m + n)
        y = (m * y2 + n * y1) / (m + n)
        return x, y

    @staticmethod
    def point_from_point_at_angle(point, distance, angle):
        x = point[0] + distance * cos(radians(angle))
        y = point[1] + distance * sin(radians(angle))
        return x, y
