import pygame
from .config import colors

class Wall:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.width = 30
        self.height = 30
        self.rect = pygame.Rect(x, y, self.width, self.height)
        self.health = 20

    def take_damage(self, amount):
        self.health -= amount

    def is_destroyed(self):
        return self.health <= 0

    def draw(self, surface):
        pygame.draw.rect(surface, colors.GRAY, self.rect)
