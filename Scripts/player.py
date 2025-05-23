import pygame
from .config import colors, screenSettings


class Player:

    def __init__(self, x, y):
        self.pos = pygame.Vector2(x, y)
        self.speed = 3
        self.radius = 15
        self.inventory = {
            "items": {},
            "resources": {
                "wood": 0,
                "stone": 0,
            }
        }
        self.health = 10
        self.max_health = 10
        self.inCombat = False
        self.combat_timer = 0
        self.heal_mult = 0
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)

    def handle_input(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.pos.y -= self.speed
        if keys[pygame.K_s]:
            self.pos.y += self.speed
        if keys[pygame.K_a]:
            self.pos.x -= self.speed
        if keys[pygame.K_d]:
            self.pos.x += self.speed

        margin = self.radius
        self.pos.x = max(margin,
                         min(self.pos.x, screenSettings.V_WIDTH - margin))
        self.pos.y = max(margin,
                         min(self.pos.y, screenSettings.V_HEIGHT - margin))

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def add_to_inventory(self, item_name):
        if 'items' not in self.inventory:
            self.inventory['items'] = {}
        self.inventory['items'][item_name] = self.inventory['items'].get(
            item_name, 0) + 1

    def get_resource(self, resource_name):
        return self.inventory['resources'].get(resource_name, 0)

    def get_resources(self):
        return {
            "wood": self.inventory['resources'].get('wood', 0),
            "stone": self.inventory['resources'].get('stone', 0),
        }

    def clear_resources(self):
        self.inventory['resources']['wood'] = 0
        self.inventory['resources']['stone'] = 0
        
    def add_resource(self, resource_name, amount):
        self.inventory['resources'][resource_name] += amount

    def sub_resource(self, resource_name, amount):
        self.inventory['resources'][resource_name] -= amount
        
    def update(self):
        if self.inCombat:
            self.combat_timer -= 1
            if self.combat_timer <= 0:
                self.inCombat = False
        else:
            self.heal_mult += 0.0005
            self.health = min(self.health + self.heal_mult, self.max_health)

    def take_damage(self, amount):
        self.health -= amount
        if not self.inCombat:
            self.inCombat = True
            self.combat_timer = 200
            self.heal_mult = 0

    def draw(self, surface):
        pygame.draw.circle(surface, colors.BLACK,
                           (int(self.pos.x), int(self.pos.y)), self.radius)
        pygame.draw.circle(surface, colors.LIGHT_BROWN, (int(self.pos.x), int(self.pos.y)), (self.radius // 1.25))

    def check_dead(self):
        if self.health <= 0:
            self.health = self.max_health
            self.clear_resources()
            self.pos = pygame.Vector2(screenSettings.V_WIDTH // 2, screenSettings.V_HEIGHT // 2)
            return True

    def get_rect(self):
        return self.rect
