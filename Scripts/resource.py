import pygame
import random
import math
from .config import colors, screenSettings
from .icons import icon_tree, icon_stone

resource_icons = {
    "tree": pygame.transform.scale(pygame.image.load(icon_tree), (60, 60)),
    "stone": pygame.transform.scale(pygame.image.load(icon_stone), (40, 40))
}

def is_far_enough(x, y, existing_resources, min_distance=60):
    for res in existing_resources:
        dx = res.rect.centerx - x
        dy = res.rect.centery - y
        distance = math.hypot(dx, dy)
        if distance < min_distance:
            return False
    return True

class Resource:
    def __init__(self, x=None, y=None, existing_resources=[]):
        self.type = random.choice(["tree", "stone"])
        self.image = resource_icons[self.type]
        self.rect = self.image.get_rect()

        if self.type == "tree":
            self.mine_time = 30
        elif self.type == "stone":
            self.mine_time = 60
        self.mine_progress = 0

    def update(self, player):
        """Update the mining progress if the player collides with the resource."""
        if player.get_rect().colliderect(self.rect):
            self.mine_progress += 1
        else:
            self.mine_progress = 0

        return self.mine_progress >= self.mine_time

    def draw(self, surface):
        surface.blit(self.image, self.rect.topleft)

        if self.mine_progress > 0:
            progress_ratio = self.mine_progress / self.mine_time
            bar_width = self.rect.width
            bar_height = 4
            bar_x = self.rect.x
            bar_y = self.rect.y - 6
            pygame.draw.rect(surface, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            pygame.draw.rect(surface, (255, 255, 0), (bar_x, bar_y, int(bar_width * progress_ratio), bar_height))
    
    def get_rect(self):
        return self.rect