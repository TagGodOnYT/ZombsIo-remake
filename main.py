import pygame
import sys
import random
from Scripts.config import screenSettings, colors
from Scripts.zombie import Zombie
from Scripts.player import Player
from Scripts.resource import Resource
from Scripts.turret import Turret
from Scripts.projectile import Projectile
from Scripts.icons import icon_game
from Scripts.impacts import Impact
from Scripts.wall import Wall
from Scripts.crafting_menu import CraftingMenu

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
canZombiesSpawn = False

# Game Time Stuff
night_count = 0
isNight = False
dayTimeLength = 30
nightTimeLength = 40
dayswitch_time_counter = 0

# Player Stuff
player = Player(screenSettings.V_WIDTH // 2, screenSettings.V_HEIGHT // 2)

# Resource Stuff
resources = []
resource_margin_x = 10
resource_margin_y = 10
resource_spawn_timer = 0
resource_spawn_interval = screenSettings.FPS * 5

for _ in range(20):
    x = random.randint(resource_margin_x,
                       screenSettings.V_WIDTH - resource_margin_x)
    y = random.randint(resource_margin_y,
                       screenSettings.V_HEIGHT - resource_margin_y)
    resources.append(Resource(x, y))

turrets = []
projectiles = []
impacts = []

walls = []

crafting_menu = CraftingMenu(player, turrets)
menu_open = False


def draw_window(menu_open=False, crafting_menu=None):
    if(isNight):
        game_surface.fill(colors.NIGHT_COLOR)
    else:
        game_surface.fill(colors.DAY_COLOR)

    for res in resources:
        res.draw(game_surface)

    for zombie in zombies:
        zombie.draw(game_surface)

    for turret in turrets:
        turret.draw(game_surface)

    for proj in projectiles:
        proj.draw(game_surface)

    for impact in impacts:
        impact.draw(game_surface)

    for wall in walls:
        wall.draw(game_surface)

    player.draw(game_surface)
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
    # health bar, should be bottom left screen but currently is bottom center
    health_bar_width = 200
    health_bar_height = 20
    health_bar_x = 10
    health_bar_y = screenSettings.V_HEIGHT - health_bar_height - 10
    health_ratio = player.health / player.max_health

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

    
    #day/night/wave info
    wave_text = font.render(f"Wave: {wave}", True, colors.WHITE)
    game_surface.blit(wave_text, (10, 50))

    if menu_open and crafting_menu is not None:
        crafting_menu.draw(game_surface)

    window_width, window_height = win.get_size()

    scale_x = window_width / screenSettings.V_WIDTH
    scale_y = window_height / screenSettings.V_HEIGHT
    scale = min(scale_x, scale_y)

    scaled_width = int(screenSettings.V_WIDTH * scale)
    scaled_height = int(screenSettings.V_HEIGHT * scale)

    vignette_surface.set_alpha(int(120 * (1 - health_ratio)))
    vignette_surface.fill((255, 0, 0))
    
    scaled_surface = pygame.transform.smoothscale(
        game_surface, (scaled_width, scaled_height))

    x_offset = (window_width - scaled_width) // 2
    y_offset = (window_height - scaled_height) // 2

    win.fill((0, 0, 0))

    win.blit(scaled_surface, (x_offset, y_offset))
    scaled_surface.blit(vignette_surface, (0, 0))
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
            if dayswitch_time_counter >= screenSettings.FPS * nightTimeLength:
                isNight = False
                dayswitch_time_counter = 0
                print("Day has started")
                
        else:
            dayswitch_time_counter += 1
            if dayswitch_time_counter >= screenSettings.FPS * dayTimeLength:
                isNight = True
                night_count += 1
                dayswitch_time_counter = 0
                print(f"Night {night_count} has started")
                
        if zombie_spawn_timer >= screenSettings.FPS * wave_wait and canZombiesSpawn and isNight:
            spawn_zombies(wave * 3)
            wave += 1
            zombie_spawn_timer = 0

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    menu_open = not menu_open

                # basic turret buy
                elif event.key == pygame.K_1 and player.get_resource('wood') >= 10:
                    turrets.append(Turret(player.pos.x, player.pos.y, "basic"))
                    player.sub_resource("wood", 10)

                # rapid turret buy
                elif event.key == pygame.K_2 and player.get_resource('wood') >= 15:
                    turrets.append(Turret(player.pos.x, player.pos.y, "rapid"))
                    player.sub_resource("wood", 15)

                # wall buy
                elif event.key == pygame.K_z and player.get_resource('wood') >= 5:
                    wall_x = int(player.pos.x // 30) * 30
                    wall_y = int(player.pos.y // 30) * 30
                    walls.append(Wall(wall_x, wall_y))
                    player.sub_resource("wood", 5)

                # Add resources
                elif event.key == pygame.K_p:
                    player.add_resource("wood", 10)
                    player.health -= 1

                # allow/disallow zombies
                elif event.key == pygame.K_o:
                    canZombiesSpawn = not canZombiesSpawn

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
                    wall.take_damage(0.2)
                    hit_wall = True
                    break

            if not hit_wall and zombie.get_rect().colliderect(
                    player.get_rect()):
                player.take_damage(1)

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
    
        zombies[:] = [z for z in zombies if z.health > 0]
        walls[:] = [w for w in walls if not w.is_destroyed()]
        
        draw_window(menu_open, crafting_menu)


if __name__ == "__main__":
    main()
