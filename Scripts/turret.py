import pygame
import math
from .config import screenSettings, colors
from .icons import TurretIcon
from .projectile import Projectile

TURRET_ICONS = {
    "basic": {
        "icon": pygame.transform.scale(pygame.image.load(TurretIcon.icon_turret_basic), (60, 60))
    },
    "rapid": {
        "icon": pygame.transform.scale(pygame.image.load(TurretIcon.icon_turret_rapid), (60, 60))
    }
}

class Turret:
    def __init__(self, x, y, turret_type="basic"):
        self.pos = pygame.Vector2(x, y)
        self.radius = 30  # Adjusted for visual clarity
        self.range = 120
        self.type = turret_type
        self.icon = TURRET_ICONS[turret_type]["icon"]
        self.original_icon = self.icon  # Keep a reference to the original icon
        if turret_type == "basic":
            self.fire_delay = 30
            self.damage = 2
        elif turret_type == "rapid":
            self.fire_delay = 15
            self.damage = 1
        self.cooldown = 0
        self.gridspaces = 4  # Assume 2x2 grid spaces

    def update(self, zombies):
        self.cooldown -= 1

        # Constrain the turret within the screen boundaries
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

    def draw(self, surface, zombies):
        # Get the closest zombie to rotate towards
        closest = None
        closest_dist = self.range
        for z in zombies:
            dist = self.pos.distance_to(z.pos)
            if dist < closest_dist:
                closest = z
                closest_dist = dist

        # If there is a closest zombie, rotate the turret towards it
        if closest:
            direction = closest.pos - self.pos
            angle = math.atan2(direction.y, direction.x)  # Angle in radians

            # Rotate the turret's image to face the target
            rotated_icon = pygame.transform.rotate(self.original_icon, -math.degrees(angle) - 90)  # Adjust the angle offset as needed

            # Get the new rect and adjust its position to keep the turret centered
            rotated_rect = rotated_icon.get_rect()
            rotated_rect.center = (int(self.pos.x), int(self.pos.y))  # Keep the turret's center at self.pos

            # Draw the rotated turret icon
            surface.blit(rotated_icon, rotated_rect.topleft)
        else:
            # If there's no target, draw the turret icon without rotation
            surface.blit(self.icon, self.get_rect().topleft)

    def get_rect(self):
        # Return the rect based on the turret's grid-based size
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)

    def get_grid_rect(self):
        # Return a rect representing the grid cell(s) occupied by the turret
        return pygame.Rect(self.pos.x - self.radius, self.pos.y - self.radius, self.radius * 2, self.radius * 2)
