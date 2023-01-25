###########
import time
import random

import kivy
from kivy.config import Config

Config.set("graphics", "width", 960)
Config.set("graphics", "height", 480)
from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.graphics import Rectangle, Line, Color
from kivy.lang import Builder
from kivy.metrics import dp
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.uix.relativelayout import RelativeLayout

from objects import Laser, Explosion, HealthBar
from player import Player
from enemy import Enemy, UFO
###########


from utils import Pad, Map
from sprite import Sprite
from utils import Util


class Game(Widget):
    FPS = 30
    dt = 1 / FPS
    factor = dt * FPS
    scroll_x = 0
    scroll_y = 0
    vibrate_x = 0
    vibrate_y = 0
    vibration_cooldown = 0
    threshold_distortion = 10
    max_distortion = threshold_distortion
    WIDTH = 0
    HEIGHT = 0
    scale = 2.5

    def __init__(self, **kwargs):
        super(Game, self).__init__(**kwargs)
        self.sprite2 = Enemy(parent=self)
        self.player = Player(parent=self)
        self.map = Map(parent=self)
        Clock.schedule_interval(self.update, 1 / self.FPS)

    def init(self):
        self.WIDTH = self.width * self.scale
        self.HEIGHT = self.height * self.scale
        self.scroll_x = (self.WIDTH - self.width) / 2
        self.scroll_y = (self.HEIGHT - self.height) / 2
        self.player.curr_pos = self.scroll_x + self.center_x, self.scroll_y + self.center_y
        self.sprite2.curr_pos = self.player.curr_x, self.player.curr_y + 120
        for i in range(1):
            UFO(parent=self, pos=self.spawn_pos())
        self.joystick1 = self.player.joystick1
        self.joystick2 = self.player.joystick2

    @property
    def SIZE(self):
        return self.WIDTH, self.HEIGHT

    @property
    def scroll(self):
        return self.scroll_x, self.scroll_y

    def vibrate(self, magnitude=1):
        self.vibration_cooldown += self.FPS // 2
        self.max_distortion = self.threshold_distortion * magnitude
        if kivy.platform == "android":
            from plyer import vibrator
            vibrator.vibrate(time=0.5)

    def spawn_pos(self):
        left, right = self.scroll_x, self.scroll_x + self.width
        bottom, top = self.scroll_y, self.scroll_y + self.height
        left_space, right_space = left, self.WIDTH - right
        bottom_space, top_space = bottom, self.HEIGHT - top
        min_w, min_h = (self.WIDTH - self.width) / 4, (self.HEIGHT - self.height) / 4
        points = []

        sub_area = [
            [0, top, left_space, top_space],
            [left, top, self.width, top_space],
            [right, top, right_space, top_space],
            [0, bottom, left_space, self.height],
            [right, bottom, right_space, self.height],
            [0, 0, left_space, bottom_space],
            [left, 0, self.width, bottom_space],
            [right, 0, right_space, bottom_space]
        ]

        for area in sub_area:
            x, y, w, h = area
            if w >= min_w and h >= min_h:
                x, y = random.randint(int(x), int(x + w)), random.randint(int(y), int(y + h))
                points.append((x, y))
        return random.choice(points)

    def update_draw(self):
        self.canvas.after.clear()
        self.canvas.clear()
        for laser in Laser.Lasers:
            laser.draw()
        for enemy in Enemy.Enemies:
            enemy.draw()
            enemy.health_bar.draw()
        for explosion in Explosion.Explosions:
            if explosion.of == "enemy":
                explosion.draw()
        self.player.draw()
        self.player.health_bar.draw()
        line = Line(rectangle=(-self.scroll_x, -self.scroll_y, *self.SIZE), width=2)
        self.canvas.after.add(line)
        self.map.draw()

    def update_controls(self):
        w = self.width * 0.2
        self.joystick1.size = w, w
        self.joystick1.pos = 20, 20
        self.joystick2.size = w, w
        self.joystick2.pos = self.width - w - 20, 20

    def update_sprites(self):
        for i, sprite in enumerate(Sprite.Sprites):
            for sprite2 in Sprite.Sprites[i + 1:]:
                if Util.is_character(sprite, sprite2):
                    if not ((sprite == self.player and isinstance(sprite2, UFO)) or
                            (sprite2 == self.player and isinstance(sprite, UFO))):
                        sprite.seperate(sprite2)
                    # sprite.seperate(sprite2)
            sprite.update()

    def update_scroll(self):
        x, y = self.player.curr_pos

        self.scroll_x = x - self.center_x
        self.scroll_y = y - self.center_y

        if self.scroll_x > self.WIDTH - self.width:
            self.scroll_x = self.WIDTH - self.width
        if self.scroll_x < 0:
            self.scroll_x = 0
        if self.scroll_y > self.HEIGHT - self.height:
            self.scroll_y = self.HEIGHT - self.height
        if self.scroll_y < 0:
            self.scroll_y = 0

    def update_vibration(self):
        if self.vibration_cooldown > 0:
            damp = (2 * self.vibration_cooldown) / self.FPS
            self.vibrate_x = self.max_distortion * random.choice([1, -1])  # * damp
            self.vibrate_y = self.max_distortion * random.choice([1, -1])  # * damp
            self.vibration_cooldown -= 1
        else:
            self.vibrate_x = 0
            self.vibrate_y = 0

    def update_widgets(self):
        self.clear_widgets()
        self.add_widget(self.joystick1)
        self.add_widget(self.joystick2)

    def update(self, dt):
        Game.dt = dt
        Game.factor = Game.dt * Game.FPS
        self.WIDTH = self.width * self.scale
        self.HEIGHT = self.height * self.scale
        self.sprite2.bound_screen()
        self.sprite2.orientation = self.player.orientation
        self.sprite2.set_direction(self.player.resultant, self.player.direction_angle)
        self.update_vibration()
        self.update_sprites()
        self.update_draw()
        self.update_scroll()
        self.update_controls()
        self.update_widgets()


class AlienQuestApp(App):
    def build(self):
        Builder.load_file("utils.kv")
        return Game()

    def on_start(self):
        self.root.init()


if __name__ == "__main__":
    AlienQuestApp().run()
