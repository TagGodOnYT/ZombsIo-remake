from Scripts.config import screenSettings, gameSettings, colors
from Scripts.zombie import Zombie
from Scripts.player import Player
from Scripts.resource import Resource, is_far_enough
from Scripts.turret import Turret
from Scripts.projectile import Projectile
from Scripts.icons import icon_game
from Scripts.impacts import Impact
from Scripts.wall import Wall
from Scripts.crafting_menu import CraftingMenu
from Scripts.floating_text import FloatingText
import pygame
import sys
import random
import math

pygame.init()

# Screen Stuff
DISPLAY_SIZE = (pygame.display.Info().current_w,
                pygame.display.Info().current_h)
win = pygame.display.set_mode(DISPLAY_SIZE, pygame.RESIZABLE)
pygame.display.set_caption("Zombois")

# Icon To Be Determined
#pygame.display.set_icon(pygame.image.load())

game_surface = pygame.Surface(
    (screenSettings.V_WIDTH, screenSettings.V_HEIGHT))
clock = pygame.time.Clock()
vignette_surface = pygame.Surface((screenSettings.V_WIDTH, screenSettings.V_HEIGHT))

# Zombie Stuff
zombies = []
wave = 1
zombie_spawn_timer = 0
wave_wait = 15
canZombiesSpawn = True

# Game Time Stuff
night_count = 0
isNight = False
dayTimeLength = 30
nightTimeLength = 40
dayswitch_time_counter = 0

# Floating text & Errors
floating_texts = []

# Player Stuff
player = Player(screenSettings.V_WIDTH // 2, screenSettings.V_HEIGHT // 2)
player_center_x = player.get_rect().centerx
player_center_y = player.get_rect().centery

# Resource Stuff
resources = []
resource_margin_x = 10
resource_margin_y = 10
resource_spawn_timer = 0
resource_spawn_interval = screenSettings.FPS * 5

def is_build_area_clear(center_x, center_y, size=30):
    build_rect = pygame.Rect(center_x - size // 2, center_y - size // 2, size, size)
    
    for res in resources:
        if build_rect.colliderect(res.get_rect()):
            return False
    for wall in walls:
        if build_rect.colliderect(wall.rect.inflate(-1, -1)):
            return False

    for turret in turrets:
        turret_rect = pygame.Rect(turret.pos.x - size // 2, turret.pos.y - size // 2, size, size)
        if build_rect.colliderect(turret_rect.inflate(-1, -1)):
            return False

    return True

pygame.mouse.set_pos(0,0)



def spawn_resources(num_resources):
    global resources
    for _ in range(num_resources):
        x = random.randint(0, screenSettings.V_WIDTH)
        y = random.randint(0, screenSettings.V_HEIGHT)
        if is_far_enough(x, y, resources, min_distance=30):
            resources.append(Resource(x, y, resources))
            
turrets = []
projectiles = []
impacts = []

walls = []

crafting_menu = CraftingMenu(player, turrets)
menu_open = False

def snap_to_grid_top_left(x, y):
    return int(x // gameSettings.GRID_SIZE) * gameSettings.GRID_SIZE, int(y // gameSettings.GRID_SIZE) * gameSettings.GRID_SIZE


def snap_to_grid_center(x, y):
    return int(x // gameSettings.GRID_SIZE) * gameSettings.GRID_SIZE + gameSettings.GRID_SIZE // 2, int(y // gameSettings.GRID_SIZE) * gameSettings.GRID_SIZE + gameSettings.GRID_SIZE // 2

def draw_window(menu_open=False, crafting_menu=None):
    if(isNight):
        game_surface.fill(colors.NIGHT_COLOR)
    else:
        game_surface.fill(colors.DAY_COLOR)

    for x in range(0, screenSettings.V_WIDTH, gameSettings.GRID_SIZE):
        pygame.draw.line(game_surface, (40, 40, 40), (x, 0), (x, screenSettings.V_HEIGHT))
    for y in range(0, screenSettings.V_HEIGHT, gameSettings.GRID_SIZE):
        pygame.draw.line(game_surface, (40, 40, 40), (0, y), (screenSettings.V_WIDTH, y))
        
    for res in resources:
        res.draw(game_surface)

    for zombie in zombies:
        zombie.draw(game_surface)

    for turret in turrets:
        turret.draw(game_surface, zombies)

    for proj in projectiles:
        proj.draw(game_surface)

    for impact in impacts:
        impact.draw(game_surface)

    for wall in walls:
        wall.draw(game_surface)
        
    health_ratio = player.health / player.max_health

    player.draw(game_surface)
    
    vignette_surface.set_alpha(int(120 * (1 - health_ratio)))
    vignette_surface.fill((255, 0, 0))
    game_surface.blit(vignette_surface, (0, 0))
    # resource texts
    font = pygame.font.SysFont(None, 24)
    wood_text = font.render(f"Wood: {player.get_resource('wood')}", True,
                            colors.WHITE)
    game_surface.blit(wood_text, (10, 10))
    stone_text = font.render(f"Stone: {player.get_resource('stone')}", True,
        colors.WHITE)
    game_surface.blit(stone_text, (10, 30))

    # Night Count Texts right above health bar
    night_text = font.render(f"Night: {night_count}", True, colors.WHITE)
    text_width = night_text.get_width()
    game_surface.blit(night_text, (screenSettings.V_WIDTH - text_width - 10, 10))
    # Health Bar
    health_bar_width = 200
    health_bar_height = 20
    health_bar_x = 10
    health_bar_y = screenSettings.V_HEIGHT - health_bar_height - 10

    pygame.draw.rect(
        game_surface, (30, 30, 30),
        (health_bar_x + 1, health_bar_y + 1, health_bar_width + 2, health_bar_height + 2)
    )
    pygame.draw.rect(
        game_surface, colors.RED,
        (health_bar_x, health_bar_y, health_bar_width, health_bar_height))
    pygame.draw.rect(
        game_surface, colors.GREEN,
        (health_bar_x, health_bar_y, int(health_bar_width * health_ratio), health_bar_height)
    )
    for ft in floating_texts:
        ft.draw(game_surface)

    
    #day/night/wave info
    wave_text = font.render(f"Wave: {wave}", True, colors.WHITE)
    game_surface.blit(wave_text, (10, 50))

    if menu_open and crafting_menu is not None:
        crafting_menu.draw(game_surface)

    
    mouse_x, mouse_y = pygame.mouse.get_pos()

    # Calculate scale and offsets same as for drawing
    window_width, window_height = win.get_size()
    scale_x = window_width / screenSettings.V_WIDTH
    scale_y = window_height / screenSettings.V_HEIGHT
    scale = min(scale_x, scale_y)
    scaled_width = int(screenSettings.V_WIDTH * scale)
    scaled_height = int(screenSettings.V_HEIGHT * scale)
    x_offset = (window_width - scaled_width) // 2
    y_offset = (window_height - scaled_height) // 2

    # Convert mouse position from window coordinates to game_surface coordinates
    game_x = (mouse_x - x_offset) / scale
    game_y = (mouse_y - y_offset) / scale

    # Snap to grid based on game surface coordinates
    grid_x, grid_y = snap_to_grid_center(game_x, game_y)

    # Check if area is clear for building
    can_place = is_build_area_clear(grid_x, grid_y)
    # Highlight the grid cell
    if can_place:
        color = (0, 255, 0, 100)  # green with alpha
    else:
        color = (255, 0, 0, 100)  # red with alpha
    rect = pygame.Rect(grid_x - gameSettings.GRID_SIZE // 2, grid_y - gameSettings.GRID_SIZE // 2, 
                       gameSettings.GRID_SIZE, gameSettings.GRID_SIZE)

    highlight_surface = pygame.Surface((gameSettings.GRID_SIZE, gameSettings.GRID_SIZE), pygame.SRCALPHA)
    highlight_surface.fill(color)
    game_surface.blit(highlight_surface, rect.topleft)
    scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_width, scaled_height))
    win.fill((0, 0, 0))
    win.blit(scaled_surface, (x_offset, y_offset))
    pygame.display.update()


def spawn_zombies(num):
    if not canZombiesSpawn and isNight:
        return
        
    margin = 15
    for _ in range(num):
        x = random.randint(margin, screenSettings.V_WIDTH - margin)
        y = random.randint(margin, screenSettings.V_HEIGHT - margin)
        zombies.append(Zombie(x, y))


def main():
    global wave, zombie_spawn_timer, resource_spawn_timer, menu_open, canZombiesSpawn, isNight, night_count, dayswitch_time_counter, nightTimeLength, dayTimeLength, wave_wait
    while True:
        clock.tick(screenSettings.FPS)

        if isNight:
            dayswitch_time_counter += 1
            zombie_spawn_timer += 1
            if zombie_spawn_timer >= screenSettings.FPS * wave_wait and canZombiesSpawn:
                spawn_zombies(wave * 3)
                wave += 1
                zombie_spawn_timer = 0
                
            if dayswitch_time_counter >= screenSettings.FPS * nightTimeLength:
                isNight = False
                dayswitch_time_counter = 0
                print("Day has started")
                
        else:
            dayswitch_time_counter += 1
            if dayswitch_time_counter >= screenSettings.FPS * dayTimeLength:
                isNight = True
                night_count += 1
                zombie_spawn_timer = 0
                dayswitch_time_counter = 0
                print(f"Night {night_count} has started")

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    menu_open = not menu_open

                # basic turret buy
                elif event.key == pygame.K_1 and player.get_resource('wood') >= 10:
                    x, y = snap_to_grid_center(player.get_rect().centerx, player.get_rect().centery)

                    if is_build_area_clear(x - gameSettings.GRID_SIZE // 2, y - gameSettings.GRID_SIZE // 2):
                        turrets.append(Turret(x, y, "basic"))
                        player.sub_resource("wood", 10)
                    else:
                        floating_texts.append(FloatingText("Cannot place here, overlaps!", x, y))

                # rapid turret buy
                elif event.key == pygame.K_2 and player.get_resource('wood') >= 15:
                    x, y = snap_to_grid_center(player.get_rect().centerx, player.get_rect().centery)
                    if is_build_area_clear(x - gameSettings.GRID_SIZE // 2, y - gameSettings.GRID_SIZE // 2):
                        turrets.append(Turret(x, y, "rapid"))
                        player.sub_resource("wood", 15)
                    else:
                        floating_texts.append(FloatingText("Cannot place here, overlaps!", x, y))

                        # wall buy
                elif event.key == pygame.K_z and player.get_resource('wood') >= 5:
                    x, y = snap_to_grid_center(player.get_rect().centerx, player.get_rect().centery)
                    if is_build_area_clear(x, y):
                        walls.append(Wall(x, y))
                        player.sub_resource("wood", 5)
                    else:
                        floating_texts.append(FloatingText("Cannot place here, overlaps!", x, y))
    
                # Add resources
                elif event.key == pygame.K_p:
                    player.add_resource("wood", 10)
                    player.take_damage(1)

                # allow/disallow zombies
                elif event.key == pygame.K_o:
                    canZombiesSpawn = not canZombiesSpawn

                elif event.key == pygame.K_l:
                    isNight = not isNight

            if menu_open:
                if event.type in [
                        pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP,
                        pygame.MOUSEMOTION
                ]:
                    window_width, window_height = win.get_size()
                    scale_x = window_width / screenSettings.V_WIDTH
                    scale_y = window_height / screenSettings.V_HEIGHT
                    scale = min(scale_x, scale_y)

                    scaled_width = int(screenSettings.V_WIDTH * scale)
                    scaled_height = int(screenSettings.V_HEIGHT * scale)

                    x_offset = (window_width - scaled_width) // 2
                    y_offset = (window_height - scaled_height) // 2

                    if hasattr(event, 'pos'):
                        mx, my = event.pos
                        gx = (mx - x_offset) / scale
                        gy = (my - y_offset) / scale
                        gx = max(0, min(gx, screenSettings.V_WIDTH))
                        gy = max(0, min(gy, screenSettings.V_HEIGHT))

                        new_event = pygame.event.Event(
                            event.type, {
                                'pos': (gx, gy),
                                'button': getattr(event, 'button', None)
                            })
                        crafting_menu.handle_event(new_event)
                else:
                    crafting_menu.handle_event(event)

        # resource_spawn_timer += 1
        # if resource_spawn_timer >= max(30, resource_spawn_interval - wave * 5):
        #     if len(resources) < 30:
        #         x = random.randint(20, screenSettings.V_WIDTH - 20)
        #         y = random.randint(20, screenSettings.V_HEIGHT - 20)
        #         resources.append(Resource(x, y))
        #     resource_spawn_timer = 0

        player.handle_input()
        for zombie in zombies:
            zombie.update(player.pos)

            hit_wall = False
            for wall in walls:
                if zombie.get_rect().colliderect(wall.rect):
                    if zombie.can_hit():
                        wall.take_damage(0.2)
                        zombie.reset_hit_cooldown()
                    hit_wall = True
                    break

            if not hit_wall and zombie.get_rect().colliderect(player.get_rect()):
                if zombie.can_hit():
                    player.take_damage(1)
                    zombie.reset_hit_cooldown()


        for turret in turrets:
            proj = turret.update(zombies)
            if proj:
                projectiles.append(proj)

        for proj in projectiles[:]:
            proj.update()
            if proj.has_hit():
                if proj.target:
                    proj.target.health -= proj.damage
                impacts.append(Impact(proj.pos))
                projectiles.remove(proj)

        for impact in impacts[:]:
            impact.update()
            if impact.is_done():
                impacts.remove(impact)

        for res in resources[:]:
            if res.update(player):
                if res.type == 'tree':
                    player.add_resource('wood', 1)
                elif res.type == 'stone':
                    player.add_resource('stone', 1)
                res.mine_progress = 0
                
        if player.check_dead():
            zombies.clear()
            turrets.clear()
            projectiles.clear()
            resources.clear()
            impacts.clear()
            floating_texts.clear()
            isNight = False
            wave = 0
            night_count = 0
    
        zombies[:] = [z for z in zombies if z.health > 0]
        walls[:] = [w for w in walls if not w.is_destroyed()]
        if len(resources) != 10:
            spawn_resources(1)
        player.update()

        for ft in floating_texts[:]:
            ft.update()
            if ft.is_expired():
                floating_texts.remove(ft)

        draw_window(menu_open, crafting_menu)


if __name__ == "__main__":
    main()