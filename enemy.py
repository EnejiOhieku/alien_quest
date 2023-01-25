import random
from math import *

from objects import Ship, HealthBar, Laser, Explosion
from sprite import Sprite


class Enemy(Ship):
    Enemies = []

    def __init__(self, **kwargs):
        super(Enemy, self).__init__("assets/imgs/enemy/enemyBlack1.png", **kwargs)
        self.health_bar = HealthBar(size=(120, 20), parent=self.parent)
        self.flame = Sprite(source="assets/imgs/rocket_flame", parent=self.parent)
        self.bound_screen()
        Enemy.Enemies.append(self)

    def kill(self):
        Sprite.Sprites.remove(self)
        Enemy.Enemies.remove(self)
        HealthBar.HealthBars.remove(self.health_bar)

    def update_health(self):
        if not self.alive():
            Explosion(self, scale=3, type=3)
            self.parent.vibrate()
            self.kill()
        if self.parent is not None:
            x = self.curr_x - self.parent.scroll_x + self.parent.vibrate_x
            y = self.curr_y + self.collision_radius + 20 - self.parent.scroll_y + self.parent.vibrate_x
            self.health_bar.center = x, y
            self.health_bar.health = self.health

    def check_hit(self):
        for laser in Laser.Lasers:
            if laser.to == "enemy" and self.collide(laser):
                laser.kill()
                self.health -= laser.damage

    def update_flame(self):
        self.flame.orientation = self.orientation
        distance = (self.flame.current.height + self.current.height) / 2
        x = self.curr_x + distance * cos(radians(self.orientation + 180))
        y = self.curr_y + distance * sin(radians(self.orientation + 180))
        self.flame.curr_pos = x, y
        if self.resultant == 0:
            if self.flame.scale >= 0:
                self.flame.scale -= 0.05
        else:
            if self.flame.scale <= self.resultant:
                self.flame.scale += 0.08
        if self.flame.scale > self.resultant:
            self.flame.scale -= 0.05

    def draw(self):
        super(Enemy, self).draw()
        self.flame.draw()

    def update(self, *args):
        self.bound_screen()
        self.update_health()
        self.update_flame()
        self.check_hit()


class UFO(Ship):

    def __init__(self, max_health=200, pos=None, **kwargs):
        super(UFO, self).__init__("assets/imgs/ufo/ufoRed.png", max_health=max_health, **kwargs)
        self.health_bar = HealthBar(size=(120, 20), parent=self.parent, max_health=max_health)
        self.spawn()
        from behaviors import behaviors
        self.__behavior = random.choice(behaviors)(self)
        self.__behavior.setup()
        self.bound_screen(restricted=False)
        Enemy.Enemies.append(self)

    def behavior(self):
        self.__behavior.update_behavior()

    def spawn(self):
        quadrant = random.randint(0, 3)
        left, bottom = int(self.collision_radius), int(self.collision_radius)
        right, top = int(self.parent.WIDTH - self.collision_radius), int(self.parent.HEIGHT - self.collision_radius)

        if quadrant == 0:
            self.start = "left"
            self.curr_x = -self.collision_radius
            self.curr_y = random.randint(bottom, top)
        elif quadrant == 1:
            self.start = "right"
            self.curr_x = self.parent.WIDTH + self.collision_radius
            self.curr_y = random.randint(bottom, top)
        elif quadrant == 2:
            self.start = "bottom"
            self.curr_x = random.randint(left, right)
            self.curr_y = -self.collision_radius
        elif quadrant == 3:
            self.start = "top"
            self.curr_x = random.randint(left, right)
            self.curr_y = self.parent.HEIGHT + self.collision_radius

    def is_alive(self):
        return self.health > 0

    @property
    def collision_radius(self):
        return self.width / 2

    def kill(self):
        Enemy.kill(self)

    def update_health(self):
        Enemy.update_health(self)

    def check_hit(self):
        Enemy.check_hit(self)

    def attack_player(self):
        player = self.parent.player
        if not player.shielded and self.collide(player):
            player.health -= 1 - (self.distance(player) / (self.collision_radius + player.collision_radius))

    def update(self, *args):
        self.draw()
        self.bound_screen(restricted=False)
        self.update_health()
        self.behavior()
        self.check_hit()
        self.attack_player()
        from main import Game
        self.orientation += 8 * Game.factor
