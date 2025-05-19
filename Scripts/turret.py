import pygame
from .config import screenSettings, colors
from .projectile import Projectile

class Turret:
    def __init__(self, x, y, turret_type="basic"):
        self.pos = pygame.Vector2(x, y)
        self.radius = 10
        self.range = 120
        self.type = turret_type
        if turret_type == "basic":
            self.fire_delay = 30
            self.damage = 1
        elif turret_type == "rapid":
            self.fire_delay = 10
            self.damage = 0.5
        self.cooldown = 0

    def update(self, zombies):
        self.cooldown -= 1

        margin = self.radius
        self.pos.x = max(margin, min(self.pos.x, screenSettings.V_WIDTH - margin))
        self.pos.y = max(margin, min(self.pos.y, screenSettings.V_HEIGHT - margin))

        if self.cooldown <= 0:
            closest = None
            closest_dist = self.range
            for z in zombies:
                dist = self.pos.distance_to(z.pos)
                if dist < closest_dist:
                    closest = z
                    closest_dist = dist
            if closest:
                self.cooldown = self.fire_delay
                return Projectile(self.pos, closest, int(self.damage))

        return None

    def draw(self, surface):
        pygame.draw.circle(surface, colors.GREEN, (int(self.pos.x), int(self.pos.y)), self.radius)
