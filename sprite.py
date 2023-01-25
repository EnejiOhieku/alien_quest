import random
from copy import copy
from math import *
from kivy.graphics import Quad, Line, Ellipse
from kivy.uix.widget import Widget
import os
from utils import Util

from PIL.Image import open


class SpriteBase:
    def __init__(self, source: str, scale=1):
        self._width, self._height = open(source).size
        self.scale = scale
        self.center_x, self.center_y = 0, 0
        self.center = [0, 0]
        self._source = source
        self._image = Quad(source=source)
        self.theta1 = Util.angle_between_points(self.corners[1], self.corners[2], self.center)
        self.theta2 = Util.angle_between_points(self.corners[0], self.corners[1], self.center)
        self._angle = self.ref_angle = self.theta1 / 2

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, source):
        self._image.source = source
        self._source = source

    @property
    def orientation(self):
        return self._angle - self.ref_angle

    @orientation.setter
    def orientation(self, value):
        self._angle = (value + self.ref_angle) % 360

    @property
    def width(self):
        return self.scale * self._width

    @property
    def height(self):
        return self.scale * self._height

    @property
    def size(self):
        return self.width, self.height

    @property
    def center(self):
        return self.center_x, self.center_y

    @center.setter
    def center(self, value):
        self.center_x, self.center_y = value

    @property
    def radius(self):
        return Util.distance_between_points(self.center, self.corners[0])

    @property
    def corners(self):
        x, y = self.pos
        w, h = self.size
        return [
            [x, y],
            [x, y + h],
            [x + w, y + h],
            [x + w, y]
        ]

    @property
    def pos(self):
        return self.center_x - self.width / 2, self.center_y - self.height / 2

    @pos.setter
    def pos(self, value):
        self.center_x = value[0] + self.width / 2
        self.center_y = value[1] + self.height / 2

    @property
    def image(self):
        img = self._image
        img.points = self.points
        return img

    @property
    def points(self):
        center_x, center_y = self.center
        points = []
        angles = [self.theta2, 180, self.theta2 + 180, 0]
        for angle in angles:
            x = center_x + self.radius * cos(radians(self._angle + angle))
            y = center_y + self.radius * sin(radians(self._angle + angle))
            points.extend([x, y])
        return points


class Sprite:
    Sprites = []

    def __init__(self, source: str, parent=None, scale=1, pos=(0, 0)):

        self.parent = parent
        self.direction_angle = 0
        self.orientation = random.randint(0, 359)
        self.ANIMATION_SPEED = 1
        self.animation_cooldown = self.ANIMATION_SPEED

        self.scale = scale
        self.source = source

        self.dx, self.dy = 0, 0
        self.curr_pos = pos
        self.bounds = None
        self.restricted = True
        Sprite.Sprites.append(self)

    @property
    def width(self):
        return self.current.width

    @property
    def height(self):
        return self.current.height

    @property
    def collision_radius(self):
        return (self.width + self.height) / 5

    def bound_screen(self, restricted=True):
        if self.parent is not None:
            self.set_bounds(*self.parent.pos, self.parent.WIDTH, self.parent.HEIGHT, restricted)

    def is_bounded(self):
        return self.bounds is not None

    def set_bounds(self, left: float, bottom: float, right: float, top: float, restricted=True):
        self.bounds = {'left': left, 'bottom': bottom, 'top': top, 'right': right}
        self.restricted = restricted

    def update_pos(self):
        from main import Game
        self.curr_x += self.dx * Game.factor
        self.curr_y += self.dy * Game.factor

        if self.is_bounded() and self.restricted:
            if self.curr_x < self.bounds['left'] + self.collision_radius:
                self.curr_x = self.bounds['left'] + self.collision_radius
            if self.curr_x > self.bounds['right'] - self.collision_radius:
                self.curr_x = self.bounds['right'] - self.collision_radius
            if self.curr_y < self.bounds['bottom'] + self.collision_radius:
                self.curr_y = self.bounds['bottom'] + self.collision_radius
            if self.curr_y > self.bounds['top'] - self.collision_radius:
                self.curr_y = self.bounds['top'] - self.collision_radius

        if self.parent is not None:
            self.current.center = self.curr_x + self.parent.vibrate_x - self.parent.scroll_x, \
                                  self.curr_y + self.parent.vibrate_y - self.parent.scroll_y

    def out_of_bounds(self, side=None):
        assert self.bounds is not None, "Sprite: bounds of sprite not set"
        if side is None:
            return self.curr_x < self.bounds['left'] - self.collision_radius or \
                   self.curr_x > self.bounds['right'] + self.collision_radius or \
                   self.curr_y < self.bounds['bottom'] - self.collision_radius or \
                   self.curr_y > self.bounds['top'] + self.collision_radius
        else:
            if side == "left":
                return self.curr_x < self.bounds['left'] - self.collision_radius
            elif side == "right":
                return self.curr_x > self.bounds['right'] + self.collision_radius
            elif side == "bottom":
                return self.curr_y < self.bounds['bottom'] - self.collision_radius
            elif side == "top":
                return self.curr_y > self.bounds['top'] + self.collision_radius
    @property
    def curr_pos(self):
        return self.curr_x, self.curr_y

    @curr_pos.setter
    def curr_pos(self, value):
        self.curr_x, self.curr_y = value

    @property
    def resultant(self):
        return (self.dx ** 2 + self.dy ** 2) ** 0.5

    def set_direction(self, magnitude, angle):
        self.dx = magnitude * cos(radians(angle))
        self.dy = magnitude * sin(radians(angle))
        self.direction_angle = angle

    @property
    def source(self):
        return self._source

    @source.setter
    def source(self, value):
        self._source = value
        self.sprite_bases = []
        self.load_images()
        self.index = 0
        self.current = copy(self.sprite_bases[self.index])

    def load_images(self):
        file = os.path.join(os.getcwd(), self.source)
        if os.path.isdir(file):
            for source in sorted(os.listdir(file)):
                self.sprite_bases.append(SpriteBase(f"{file}/{source}", self.scale))
        else:
            self.sprite_bases = [SpriteBase(file, self.scale)]

    def distance(self, sprite):
        return Util.distance_between_points(self.curr_pos, sprite.curr_pos)

    def collide(self, sprite):
        return self.collision_radius + sprite.collision_radius >= self.distance(sprite)

    def seperate(self, sprite):
        if not Util.is_character(self, sprite):
            return

        if sprite is not self and self.collide(sprite):
            first, second = self, sprite
            r1, r2 = first.collision_radius, second.collision_radius
            target_distance = r1 + r2
            m, n = r1 / target_distance, r2 / target_distance
            center = Util.point_of_internal_division(first.curr_pos, second.curr_pos, m, n)
            if first.distance(second) == 0:
                first_inclination = random.randint(0, 180)
                second_inclination = first_inclination + 180
            else:
                first_inclination = Util.two_point_line_inclination(center, first.curr_pos)
                second_inclination = Util.two_point_line_inclination(center, second.curr_pos)
            first.curr_pos = Util.point_from_point_at_angle(center, r1, first_inclination)
            second.curr_pos = Util.point_from_point_at_angle(center, r2, second_inclination)

    def stop(self):
        self.dx, self.dy = 0, 0

    def kill(self):
        Sprite.Sprites.remove(self)

    def draw(self):
        if len(self.sprite_bases) > 1:
            if self.animation_cooldown <= 0:
                self.animation_cooldown = self.ANIMATION_SPEED
                self.index = (self.index + 1) % len(self.sprite_bases)
                self.current = copy(self.sprite_bases[self.index])
            else:
                self.animation_cooldown -= 1

        self.orientation %= 360
        self.current.orientation = self.orientation
        self.current.scale = self.scale
        self.update_pos()
        # r = Line(circle=(*self.center, self.collision_radius))
        # self.canvas.add(r)
        if self.parent is not None:
            self.parent.canvas.add(self.current.image)

    def update(self, *args):
        pass
