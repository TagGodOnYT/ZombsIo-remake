import pygame
from .config import colors
from .turret import Turret

class CraftingMenu:
    def __init__(self, player, turrets):
        self.player = player
        self.turrets = turrets
        self.tabs = ["Items", "Turrets"]
        self.active_tab = 0
        self.font = pygame.font.SysFont(None, 20)
        self.selected_item = None

        self.tab_height = 30
        self.item_box_height = 60
        self.item_box_width = 200

        self.turret_types = [
            {'name': 'Basic Turret', 'type': 'basic', 'cost': 10},
            {'name': 'Rapid Turret', 'type': 'rapid', 'cost': 15},
        ]

    def draw(self, surface):
        menu_width = 220
        menu_height = 300
        x = 10
        y = 80

        pygame.draw.rect(surface, colors.DARK_GREY, (x, y, menu_width, menu_height))

        for i, tab in enumerate(self.tabs):
            tab_color = colors.LIGHT_GREY if i == self.active_tab else colors.BLACK
            pygame.draw.rect(surface, tab_color, (x + i * (menu_width // 2), y, menu_width // 2, self.tab_height))
            text = self.font.render(tab, True, colors.WHITE)
            surface.blit(text, (x + i * (menu_width // 2) + 10, y + 5))

        items = self.get_items()
        for i, item in enumerate(items):
            item_y = y + self.tab_height + i * self.item_box_height
            rect = pygame.Rect(x, item_y, self.item_box_width, self.item_box_height)
            pygame.draw.rect(surface, colors.LIGHT_GREY if item == self.selected_item else colors.BLACK, rect)
            text = self.font.render(item['name'], True, colors.WHITE)
            surface.blit(text, (x + 10, item_y + 10))
            cost_text = self.font.render(f"Cost: {item['cost']} wood", True, colors.WHITE)
            surface.blit(cost_text, (x + 10, item_y + 30))

    def get_items(self):
        if self.active_tab == 0:
            return []  # You can add items like swords here
        elif self.active_tab == 1:
            return self.turret_types

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            menu_x = 10
            menu_y = 80

            if menu_y <= y <= menu_y + self.tab_height:
                tab_index = (x - menu_x) // (220 // 2)
                if 0 <= tab_index < len(self.tabs):
                    self.active_tab = tab_index
                    self.selected_item = None
                    return

            item_start_y = menu_y + self.tab_height
            for i, item in enumerate(self.get_items()):
                item_rect = pygame.Rect(menu_x, item_start_y + i * self.item_box_height, self.item_box_width, self.item_box_height)
                if item_rect.collidepoint(x, y):
                    self.selected_item = item
                    return

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and self.selected_item:
                self.craft_selected()

    def craft_selected(self):
        if self.active_tab == 1 and self.selected_item:
            cost = self.selected_item.get('cost', 0)
            if self.player.inventory["wood"] >= cost:
                turret_type = self.selected_item.get('type', 'basic')
                new_turret = Turret(self.player.pos.x, self.player.pos.y, turret_type)
                self.turrets.append(new_turret)
                self.player.inventory["wood"] -= cost
