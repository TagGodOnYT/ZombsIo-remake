import pygame
from .config import colors

class Wall:
    def __init__(self, center_x, center_y):
        self.width = 30
        self.height = 30
        self.pos = pygame.Vector2(center_x - self.width // 2, center_y - self.height // 2)
        self.rect = pygame.Rect(self.pos.x, self.pos.y, self.width, self.height)
        self.health = 20

    def take_damage(self, amount):
        self.health -= amount

    def is_destroyed(self):
        return self.health <= 0

    def draw(self, surface):
        pygame.draw.rect(surface, colors.GRAY, self.rect)

    def get_rect(self):
        return self.rect