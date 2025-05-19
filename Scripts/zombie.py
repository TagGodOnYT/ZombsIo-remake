import pygame
import random
from .config import colors, screenSettings

class Zombie:
    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.speed = 1.2
        self.radius = 12
        self.health = 3
        self.max_health = 3

    def update(self, player_pos):
        direction = (player_pos - self.pos).normalize()
        self.pos += direction * self.speed
        
        margin = self.radius
        self.pos.x = max(margin, min(self.pos.x, screenSettings.V_WIDTH - margin))
        self.pos.y = max(margin, min(self.pos.y, screenSettings.V_HEIGHT - margin))
        
    def draw(self, surface):
        pygame.draw.circle(surface, colors.GRAY, (int(self.pos.x), int(self.pos.y)), self.radius)
        if self.health < self.max_health:
            bar_width = self.radius
            bar_height = 4
            bar_x = self.pos.x
            bar_y = self.pos.y - 6
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (255, 255, 0), (bar_x, bar_y, int(bar_width * self.health), bar_height))

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                           self.radius * 2, self.radius * 2)
