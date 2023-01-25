import math
import random

from enemy import UFO, Enemy
from utils import Util


class UfoType:
    def __init__(self, ufo: UFO):
        self.ufo = ufo

    def setup(self):
        pass

    def update_behavior(self):
        pass


class UfoType_1:
    def __init__(self, ufo: UFO):
        # move horizontally and vertically
        self.ufo = ufo
        self.ufo.value = 5
        self.speed = 2

    def setup(self):
        if self.ufo.start == "left":
            self.ufo.set_direction(self.speed, 0)
        elif self.ufo.start == "right":
            self.ufo.set_direction(self.speed, 180)
        elif self.ufo.start == "top":
            self.ufo.set_direction(self.speed, 270)
        elif self.ufo.start == "bottom":
            self.ufo.set_direction(self.speed, 90)

    def update_behavior(self):
        if self.ufo.out_of_bounds("left") and self.ufo.start == "right" or \
                self.ufo.out_of_bounds("right") and self.ufo.start == "left" or \
                self.ufo.out_of_bounds("bottom") and self.ufo.start == "top" or \
                self.ufo.out_of_bounds("top") and self.ufo.start == "bottom":
            self.ufo.kill()


class UfoType_2:
    def __init__(self, ufo: UFO):
        # move diagonally
        self.ufo = ufo
        self.ufo.value = 10
        self.speed = 2

    def setup(self):
        if self.ufo.start == "left":
            angles = [45, -45]
        elif self.ufo.start == "right":
            angles = [135, -135]
        elif self.ufo.start == "top":
            angles = [-45, -135]
        else:  # bottom
            angles = [45, 135]
        angle = random.choice(angles)
        offset = random.randint(-5, 5)
        self.ufo.set_direction(self.speed, angle + offset)

    def update_behavior(self):
        if self.ufo.out_of_bounds("left") and self.ufo.start in ["right", "top", "bottom"] or \
                self.ufo.out_of_bounds("right") and self.ufo.start in ["left", "top", "bottom"] or \
                self.ufo.out_of_bounds("bottom") and self.ufo.start in ["right", "top", "left"] or \
                self.ufo.out_of_bounds("top") and self.ufo.start in ["right", "left", "bottom"]:
            self.ufo.kill()


class UfoType_3:
    def __init__(self, ufo: UFO):
        # move directly towards player
        self.ufo = ufo
        self.ufo.value = 15
        self.speed = 1.6

    def setup(self):
        pass

    def update_behavior(self):
        player = self.ufo.parent.player
        angle = Util.two_point_line_inclination(self.ufo.curr_pos, player.curr_pos)
        self.ufo.set_direction(self.speed, angle)


class UfoType_4:
    def __init__(self, ufo: UFO):
        # circle around player
        self.ufo = ufo
        self.ufo.value = 30
        self.speed = 1.5
        self.rotation_speed = 3.5

    def setup(self):
        pass

    def update_behavior(self):
        player = self.ufo.parent.player
        angle = Util.two_point_line_inclination(self.ufo.curr_pos, player.curr_pos)
        d = Util.distance_between_points(self.ufo.curr_pos, player.curr_pos)
        if d < player.collision_radius / 2:
            factor = d / (player.collision_radius + self.ufo.collision_radius)
            speed = factor * self.speed
            rotation_speed = factor * self.rotation_speed
        else:
            speed = self.speed
            rotation_speed = self.rotation_speed

        self.ufo.dx = speed * math.cos(math.radians(angle)) + rotation_speed * math.cos(math.radians(angle - 90))
        self.ufo.dy = speed * math.sin(math.radians(angle)) + rotation_speed * math.sin(math.radians(angle - 90))


class UfoType_5:
    def __init__(self, ufo: UFO):
        # speedy random direction
        self.ufo = ufo
        self.ufo.value = 35

    def setup(self):
        if random.random() > 0.5:
            if self.ufo.start == "left":
                angle = 0
            elif self.ufo.start == "right":
                angle = 180
            elif self.ufo.start == "top":
                angle = 270
            else:  # bottom
                angle = 90
        else:
            rand = random.randint(0, 1)
            if self.ufo.start == "left":
                angle = 45 if rand else -45
            elif self.ufo.start == "right":
                angle = 135 if rand else -135
            elif self.ufo.start == "top":
                angle = -45 if rand else -135
            else:  # bottom
                angle = 45 if rand else 135
        self.ufo.set_direction(5, angle)

    def update_behavior(self):
        UfoType_2.update_behavior(self)


class UfoType_6:
    def __init__(self, ufo: UFO):
        # move diagonally
        self.ufo = ufo
        self.ufo.value = 20
        self.speed = 2

    def setup(self):
        if self.ufo.start == "left":
            angle = 0
        elif self.ufo.start == "right":
            angle = 180
        elif self.ufo.start == "top":
            angle = 270
        else:  # bottom
            angle = 90
        self.direction = angle

    def update_behavior(self):
        speed = self.speed * random.randint(1, 2)
        self.direction += random.uniform(-10, 10)
        self.ufo.dx = speed * math.cos(math.radians(self.direction))
        self.ufo.dy = speed * math.sin(math.radians(self.direction))
        UfoType_2.update_behavior(self)


#behaviors = [UfoType_1, UfoType_2, UfoType_3, UfoType_4, UfoType_5, UfoType_6]
behaviors = [UfoType_4]