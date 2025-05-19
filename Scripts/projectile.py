import pygame
from .config import colors

class Projectile:
    def __init__(self, pos, target, damage=1):
        self.pos = pygame.Vector2(pos)
        self.target = target
        self.speed = 6
        self.radius = 4
        self.damage = damage


    def update(self):
        if self.target is None:
            return
        direction = (self.target.pos - self.pos).normalize()
        self.pos += direction * self.speed

    def draw(self, surface):
        end = (int(self.pos.x), int(self.pos.y))
        start = (int(self.pos.x - 4), int(self.pos.y - 4))
        pygame.draw.line(surface, (255, 0, 0), start, end, 2)
        pygame.draw.circle(surface, (255, 50, 50), end, self.radius)


    def has_hit(self):
        if self.target and self.target.get_rect().collidepoint(self.pos.x, self.pos.y):
            return True
        return False
