import pygame
from .config import colors

class FloatingText:
  def __init__(self, text, x, y, color=colors.RED, lifetime=60):
      self.text = text
      self.pos = pygame.math.Vector2(x, y)
      self.start_y = y
      self.lifetime = lifetime
      self.max_lifetime = lifetime
      self.color = color
      self.alpha = 255
      self.font = pygame.font.SysFont(None, 20)

  def update(self):
      self.lifetime -= 1
      self.pos.y -= 0.5
      self.alpha = max(0, int(255 * (self.lifetime / self.max_lifetime)))

  def draw(self, surface):
      text_surface = self.font.render(self.text, True, self.color)
      text_surface.set_alpha(self.alpha)
      surface.blit(text_surface, (self.pos.x, self.pos.y))

  def is_expired(self):
      return self.lifetime <= 0
