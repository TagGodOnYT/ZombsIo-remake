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

        self.hit_cooldown = 30
        self.cooldown_timer = 0

    def update(self, player_pos):
        direction = (player_pos - self.pos).normalize()
        self.pos += direction * self.speed

        margin = self.radius
        self.pos.x = max(margin,
                         min(self.pos.x, screenSettings.V_WIDTH - margin))
        self.pos.y = max(margin,
                         min(self.pos.y, screenSettings.V_HEIGHT - margin))
        
        if self.cooldown_timer > 0:
            self.cooldown_timer -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, colors.GRAY,
                           (int(self.pos.x), int(self.pos.y)), self.radius)

        # Only draw health bar if not at full health
        if self.health < self.max_health:
            bar_width = self.radius * 2
            bar_height = 4
            health_ratio = self.health / self.max_health

            bar_x = self.pos.x - bar_width / 2
            bar_y = self.pos.y - self.radius - 8

            # Background
            pygame.draw.rect(surface, (50, 50, 50),
                             (bar_x, bar_y, bar_width, bar_height))
            # Health
            pygame.draw.rect(
                surface, (255, 255, 0),
                (bar_x, bar_y, bar_width * health_ratio, bar_height))


    def can_hit(self):
        return self.cooldown_timer <= 0

    def reset_hit_cooldown(self):
        self.cooldown_timer = self.hit_cooldown

    def get_rect(self):
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius,
                           self.radius * 2, self.radius * 2)
