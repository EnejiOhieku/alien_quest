import random

from kivy.graphics import Rectangle
from kivy.properties import NumericProperty, StringProperty
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.clock import Clock

from sprite import Sprite
from math import *
from utils import Pad, Util
import os


class HealthBar:
    HealthBars = []

    def __init__(self, parent=None, max_health=100, pos=(0, 0), size=(0, 0)):
        self.parent = parent
        self.max_health = max_health
        self.health = max_health
        self.pos = pos
        self.size = size
        HealthBar.HealthBars.append(self)

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        template = os.path.join(os.getcwd(), "assets/imgs/healthbar/{}.png")
        self._health = value

        if self._health > self.max_health:
            self._health = self.max_health
        elif self._health < 0:
            self._health = 0

        if self.health > self.max_health * 0.75:
            color = "green"
        elif self.health > self.max_health * 0.50:
            color = "blue"
        elif self.health > self.max_health * 0.25:
            color = "orange"
        else:
            color = "red"
        self.current_source = template.format(color)

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

    @property
    def center(self):
        return self.x + self.width / 2, self.y + self.height / 2

    @center.setter
    def center(self, value):
        self.pos = value[0] - self.width / 2, value[1] - self.height / 2

    def draw(self):
        margin = self.width * 0.04
        bar_length = (self.width - margin * 2) * self.health / self.max_health
        bar_height = self.height - margin * 2

        frame = Rectangle(pos=self.pos, size=self.size,
                          source=os.path.join(os.getcwd(), "assets/imgs/healthbar/frame.png"))
        bar = Rectangle(pos=(self.x + margin, self.y + margin), size=(bar_length, bar_height),
                        source=self.current_source)
        if self.parent is not None:
            self.parent.canvas.add(frame)
            self.parent.canvas.add(bar)


class Explosion(Sprite):
    Explosions = []

    def __init__(self, ship, scale=1, type=1):
        super(Explosion, self).__init__(f"assets/imgs/explosion/{type}", parent=ship.parent, scale=scale,
                                        pos=ship.curr_pos)
        self.count = 0
        from player import Player
        if isinstance(ship, Player):
            self.of = "player"
        else:
            self.of = "enemy"
        Explosion.Explosions.append(self)

    def kill(self):
        Explosion.Explosions.remove(self)
        Sprite.Sprites.remove(self)

    def update(self):
        self.count += 1
        if self.count >= len(self.sprite_bases) * self.ANIMATION_SPEED:
            self.kill()


class Ship(Sprite):

    def __init__(self, source, max_health=100, **kwargs):
        Sprite.__init__(self, source, **kwargs)
        self.max_health = max_health
        self._health = max_health
        self.fire_power = 1  # can be 1, 2 or 3
        self.fire_cooldown = 30
        self.fire_counter = 0

    @property
    def health(self):
        return self._health

    @health.setter
    def health(self, value):
        self._health = value

        if self._health > self.max_health:
            self._health = self.max_health
        elif self._health < 0:
            self._health = 0

    def alive(self):
        return self._health > 0

    def at_boundary(self, bound: str):
        """
        check if sprite is at the bounds set in the boundaries,
         which can be left, right, top or bottom.
        :param bound: an option between left, right, top, bottom
        :return: boolean
        """
        if bound == "left":
            left = self.curr_x - self.collision_radius
            return left <= self.bounds["left"]
        if bound == "right":
            right = self.curr_x + self.collision_radius
            return right >= self.bounds["right"]
        if bound == "bottom":
            bottom = self.curr_x - self.collision_radius
            return bottom <= self.bounds["bottom"]
        if bound == "top":
            top = self.curr_x + self.collision_radius
            return top >= self.bounds["top"]
        raise Exception("invalid bound argument")

    def fire(self):
        if self.fire_counter >= self.fire_cooldown:
            Laser(self.fire_power, self)
            self.fire_counter = 0
        else:
            self.fire_counter += 1


class Laser(Sprite):
    Lasers = []
    speed = 20

    def __init__(self, level: int, ship):
        assert 1 <= level <= 3

        from player import Player

        if isinstance(ship, Player):
            i = 0
            self.to = "enemy"
        else:
            i = 1
            self.to = "player"
        types = {
            1: {'color': 'red', 'damage': 20},
            2: {'color': 'green', 'damage': 35},
            3: {'color': 'blue', 'damage': 50}
        }
        super(Laser, self).__init__(f"assets/imgs/lasers/{types[level]['color']}{i}.png", parent=ship.parent)
        self.damage = types[level]['damage']
        pos = Util.point_from_point_at_angle(ship.curr_pos, ship.height / 2, ship.orientation)
        self.curr_pos = pos
        self.orientation = ship.orientation
        self.set_direction(self.speed, ship.orientation)
        self.bound_screen(restricted=False)
        Laser.Lasers.append(self)

    def kill(self):
        Laser.Lasers.remove(self)
        Sprite.Sprites.remove(self)

    def update(self, *args):
        if self.parent is not None:
            self.bound_screen(restricted=False)
            if self.out_of_bounds():
                self.kill()
