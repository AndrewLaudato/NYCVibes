import pygame
import sys
import random
import os
from pygame.locals import *

# === A: Constants ===
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
MAP_DISPLAY_WIDTH = 1600
MAP_DISPLAY_HEIGHT = 1200
PLAYER_SIZE = (50, 50)
ITEM_SIZE = (64, 64)
PLAYER_SPEED = 4
SPAWN_INTERVAL_MS = 3000
SUN_DURATION_MS = 10000
FONT_SIZE = 32
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

DEVIL_SPEED = 2
DEVIL_SPAWN_CHANCE = 0.25
DEVIL_MIN_INTERVAL = 10000
DEVIL_LIFESPAN = 10000

# === B: Initialization ===
pygame.init()
pygame.mixer.init()
pygame.display.set_caption("NYC Vibe Quest")
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)

# === C: Helper Functions ===
def load_image(name, size=None):
    path = os.path.join("static", name)
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size) if size else image

def load_sound(name):
    path = os.path.join("static", name)
    return pygame.mixer.Sound(path)

def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                return

def animate_ride(vertical_shift, vehicle_image):
    frames = 30
    start_y = player_rect.y
    end_y = max(0, min(map_rect.height - PLAYER_SIZE[1], start_y + vertical_shift))
    delta_y = (end_y - start_y) / frames
    vehicle_rect = vehicle_image.get_rect(center=player_rect.center)

    for i in range(frames):
        player_rect.y = int(start_y + delta_y * i)
        vehicle_rect.centery = player_rect.centery

        camera_x = max(0, min(player_rect.centerx - SCREEN_WIDTH // 2, map_rect.width - SCREEN_WIDTH))
        camera_y = max(0, min(player_rect.centery - SCREEN_HEIGHT // 2, map_rect.height - SCREEN_HEIGHT))

        screen.blit(map_img, (-camera_x, -camera_y))
        for h in hotspots:
            screen.blit(h['img'], (h['rect'].x - camera_x, h['rect'].y - camera_y))
        if devil:
            screen.blit(devil_img, (devil.x - camera_x, devil.y - camera_y))
        screen.blit(vehicle_image, (vehicle_rect.x - camera_x, vehicle_rect.y - camera_y))
        screen.blit(player_img, (player_rect.x - camera_x, player_rect.y - camera_y))
        vibes_text = font.render(f"Vibes: {vibes}", True, WHITE, BLACK)
        screen.blit(vibes_text, (10, 10))
        if sun_active:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((255, 255, 180))
            screen.blit(overlay, (0, 0))
            sun_text = font.render("\u2600\ufe0f Double Points Active!", True, BLACK)
            screen.blit(sun_text, (SCREEN_WIDTH//2 - sun_text.get_width()//2, 10))
        pygame.display.flip()
        pygame.time.delay(20)

def show_start_screen():
    screen.blit(start_screen_img, (0, 0))
    pygame.display.flip()
    wait_for_key()

# === D: Asset Loading ===
map_img = load_image("NYCmap.jpg", (MAP_DISPLAY_WIDTH, MAP_DISPLAY_HEIGHT))
map_rect = map_img.get_rect()
player_img = load_image("KJK.png", PLAYER_SIZE)
devil_img = load_image("devil.png", ITEM_SIZE)
taxi_img = load_image("taxi.png", ITEM_SIZE)
subway_img = load_image("subway.png", ITEM_SIZE)

start_screen_img = load_image("start_screen.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
win_screen_img = load_image("win_screen.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
lose_screen_img = load_image("lose_screen.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))

hotspot_types = [
    {"name": "pretzel", "points": 4, "img": load_image("pretzel.png", ITEM_SIZE)},
    {"name": "dog", "points": 3, "img": load_image("dog.png", ITEM_SIZE)},
    {"name": "taxi", "points": 2, "img": taxi_img},
    {"name": "poop", "points": -5, "img": load_image("poop.png", ITEM_SIZE)},
    {"name": "construction", "points": -3, "img": load_image("construction.png", ITEM_SIZE)},
    {"name": "rain", "points": -4, "img": load_image("rain.png", ITEM_SIZE)},
    {"name": "sun", "points": 0, "img": load_image("sun.png", ITEM_SIZE)},
    {"name": "subway", "points": 2, "img": subway_img}
]

positive_sound = load_sound("positive.wav")
negative_sound = load_sound("negative.wav")

# === E: Main Game Loop ===
while True:
    pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
    pygame.mixer.music.play(-1)
    music_muted = False

    show_start_screen()

    player_rect = player_img.get_rect(center=map_rect.center)
    hotspots = []
    devil = None
    sun_active = False
    sun_timer = 0
    vibes = 10

    last_devil_spawn = 0
    devil_spawned_at = 0

    pygame.time.set_timer(USEREVENT+1, SPAWN_INTERVAL_MS)
    pygame.time.set_timer(USEREVENT+2, 4000)

    game_over = False

    while not game_over:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == USEREVENT+1:
                hotspot = random.choice(hotspot_types)
                attempts = 0
                while attempts < 20:
                    rect = hotspot['img'].get_rect(
                        topleft=(random.randint(0, map_rect.width - ITEM_SIZE[0]),
                                 random.randint(0, map_rect.height - ITEM_SIZE[1])))
                    if rect.colliderect(player_rect) or any(rect.colliderect(h['rect']) for h in hotspots) or (devil and rect.colliderect(devil)):
                        attempts += 1
                    else:
                        hotspots.append({**hotspot, "rect": rect})
                        break
            elif event.type == USEREVENT+2 and devil is None:
                now = pygame.time.get_ticks()
                if now - last_devil_spawn >= DEVIL_MIN_INTERVAL and random.random() < DEVIL_SPAWN_CHANCE:
                    devil = devil_img.get_rect(
                        topleft=(random.randint(0, map_rect.width - ITEM_SIZE[0]),
                                 random.randint(0, map_rect.height - ITEM_SIZE[1])))
                    devil_spawned_at = now
                    last_devil_spawn = now
                    pygame.mixer.music.load(os.path.join("static", "dark.mp3"))
                    pygame.mixer.music.play(-1)
            elif event.type == KEYDOWN and event.key == K_m:
                music_muted = not music_muted
                pygame.mixer.music.set_volume(0 if music_muted else 1)

        keys = pygame.key.get_pressed()
        player_rect.move_ip(
            (keys[K_RIGHT] - keys[K_LEFT]) * PLAYER_SPEED,
            (keys[K_DOWN] - keys[K_UP]) * PLAYER_SPEED)
        player_rect.clamp_ip(map_rect)

        if devil:
            dx = DEVIL_SPEED if devil.x < player_rect.x else -DEVIL_SPEED
            dy = DEVIL_SPEED if devil.y < player_rect.y else -DEVIL_SPEED
            devil.move_ip(dx, dy)
            if player_rect.colliderect(devil):
                vibes -= 15
                negative_sound.play()
                devil = None
                pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
                pygame.mixer.music.play(-1)

            if pygame.time.get_ticks() - devil_spawned_at > DEVIL_LIFESPAN:
                devil = None
                pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
                pygame.mixer.music.play(-1)

        camera_x = max(0, min(player_rect.centerx - SCREEN_WIDTH // 2, map_rect.width - SCREEN_WIDTH))
        camera_y = max(0, min(player_rect.centery - SCREEN_HEIGHT // 2, map_rect.height - SCREEN_HEIGHT))
        screen.blit(map_img, (-camera_x, -camera_y))

        for h in hotspots[:]:
            if player_rect.colliderect(h['rect']):
                if h['name'] == "sun":
                    sun_active = True
                    sun_timer = pygame.time.get_ticks()
                    positive_sound.play()
                else:
                    pts = h['points'] * (2 if sun_active and h['points'] > 0 else 1)
                    vibes += pts
                    if pts > 0:
                        positive_sound.play()
                    elif pts < 0:
                        negative_sound.play()

                if h['name'] == "taxi" or h['name'] == "subway":
                    shift = map_rect.height // 2
                    animate_ride(shift if player_rect.centery < map_rect.centery else -shift,
                                 taxi_img if h['name'] == "taxi" else subway_img)
                    if devil:
                        devil = None
                        pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
                        pygame.mixer.music.play(-1)

                hotspots.remove(h)
            else:
                screen.blit(h['img'], (h['rect'].x - camera_x, h['rect'].y - camera_y))

        if sun_active and pygame.time.get_ticks() - sun_timer > SUN_DURATION_MS:
            sun_active = False

        screen.blit(player_img, (player_rect.x - camera_x, player_rect.y - camera_y))
        if devil:
            screen.blit(devil_img, (devil.x - camera_x, devil.y - camera_y))

        vibes_text = font.render(f"Vibes: {vibes}", True, WHITE, BLACK)
        screen.blit(vibes_text, (10, 10))
        if sun_active:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((255, 255, 180))
            screen.blit(overlay, (0, 0))
            sun_text = font.render("\u2600\ufe0f Double Points Active!", True, BLACK)
            screen.blit(sun_text, (SCREEN_WIDTH//2 - sun_text.get_width()//2, 10))

        pygame.display.flip()

        if vibes >= 50:
            result_text = "win"
            game_over = True
        elif vibes <= 0:
            result_text = "lose"
            game_over = True

    if result_text == "win":
        screen.blit(win_screen_img, (0, 0))
    else:
        screen.blit(lose_screen_img, (0, 0))
    pygame.display.flip()
    wait_for_key()
