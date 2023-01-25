from objects import Ship, Explosion, HealthBar, Laser
from sprite import Sprite
from utils import Pad


class Player(Ship):
    max_speed = 5

    def __init__(self, **kwargs):
        super(Player, self).__init__("assets/imgs/player/playerShip3_blue.png", max_health=200, **kwargs)
        self.joystick1 = Pad()
        self.joystick2 = Pad()
        self.health_bar = HealthBar(parent=self.parent, max_health=self.max_health, size=(250, 50))
        self.shield = Sprite(source="assets/imgs/shield", parent=self.parent)
        self.shield_timer = 5
        self.shielded = False

    def joystick_clicked(self, num: int):
        if num == 1:
            return self.joystick1.magnitude != 0 and self.joystick1.angle != 0
        elif num == 2:
            return self.joystick2.magnitude != 0 and self.joystick2.angle != 0
        else:
            raise Exception("wrong argument num is either 1 or 2")

    def check_hit(self):
        for laser in Laser.Lasers:
            if laser.to == "player" and self.collide(laser):
                laser.kill()
                self.health -= laser.damage

    def update_pos(self):
        super(Player, self).update_pos()
        self.bound_screen()
        if self.joystick_clicked(1):
            self.set_direction(self.joystick1.magnitude * self.max_speed, self.joystick1.angle)
            self.orientation = self.joystick1.angle
        else:
            self.stop()

        if self.joystick_clicked(2):
            self.orientation = self.joystick2.angle
            if self.joystick2.magnitude > 0.7:
                self.fire()
        else:
            self.fire_counter = self.fire_cooldown

    def update_health(self):
        if not self.alive():
            Explosion(self, scale=3, type=3)
            self.parent.vibrate()
            self.health = self.max_health
        self.health_bar.pos = 0, self.parent.height - self.health_bar.height
        self.health_bar.health = self.health

    def draw(self):
        if self.shielded:
            self.shield.curr_pos = self.curr_pos
            self.shield.orientation = self.orientation
            self.shield.draw()
        super(Player, self).draw()

    def update(self, *args):
        self.update_pos()
        self.check_hit()
        self.update_health()