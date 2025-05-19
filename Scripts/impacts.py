import pygame

class Impact:
    def __init__(self, pos):
        self.pos = pygame.Vector2(pos)
        self.radius = 12
        self.alpha = 255
        self.surface = pygame.Surface((self.radius*2, self.radius*2), pygame.SRCALPHA)

    def update(self):
        self.alpha -= 10
        if self.alpha < 0:
            self.alpha = 0

    def draw(self, surface):
        self.surface.fill((0, 0, 0, 0))
        pygame.draw.circle(self.surface, (255, 150, 0, self.alpha), (self.radius, self.radius), self.radius)
        surface.blit(self.surface, (self.pos.x - self.radius, self.pos.y - self.radius))

    def is_done(self):
        return self.alpha == 0
