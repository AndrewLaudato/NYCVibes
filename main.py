# NYC Vibe Quest - Refactored
# Andrew Laudato - April 2025

import pygame
import sys
import random
import os
from pygame.locals import *

# === A: Constants ===
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 800
MAP_DISPLAY_WIDTH = 1365
MAP_DISPLAY_HEIGHT = 2048  # approximate vertical resolution from image
PLAYER_SIZE = (50, 50)
ITEM_SIZE = (64, 64)
PLAYER_SPEED = 4
SPAWN_INTERVAL_MS = 3000
DOG_TIMER_MS = 6000
EDIBLE_DURATION_MS = 5000
SUN_DURATION_MS = 10000
FONT_SIZE = 32

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

DEVIL_SPEED = 2
DEVIL_SPAWN_CHANCE = 0.25
DEVIL_MIN_INTERVAL = 10000
DEVIL_LIFESPAN = 10000

# === B: Game State ===
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player_rect = player_img.get_rect(center=map_rect.center)
        self.hotspots = []
        self.timed_events = []
        self.devil = None
        self.sun_active = False
        self.sun_timer = 0
        self.edible_timers = []
        self.vibes = 10
        self.last_devil_spawn = 0
        self.devil_spawned_at = 0
        self.music_muted = False
        self.game_over = False
        self.result_text = ""
        self.inventory = []
        self.devil_disabled = False

    def apply_edible(self):
        self.edible_timers.append(pygame.time.get_ticks())

    def is_high(self):
        now = pygame.time.get_ticks()
        self.edible_timers = [t for t in self.edible_timers if now - t < EDIBLE_DURATION_MS]
        return len(self.edible_timers) > 0

# === C: Initialization ===
pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("NYC Vibe Quest")
clock = pygame.time.Clock()
font = pygame.font.SysFont(None, FONT_SIZE)

# === D: Helper Functions ===
def load_image(name, size=None):
    path = os.path.join("static", name)
    image = pygame.image.load(path).convert_alpha()
    return pygame.transform.scale(image, size) if size else image

def load_sound(name):
    return pygame.mixer.Sound(os.path.join("static", name))

def wait_for_key():
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == KEYDOWN:
                return

def schedule_event(state, delay_ms, callback):
    state.timed_events.append((pygame.time.get_ticks() + delay_ms, callback))

def spawn_poop(state, rect):
    state.hotspots.append({"name": "poop", "points": -5, "img": poop_img, "rect": rect})

# === E: Load Assets ===
map_img = load_image("NYCmap.jpg", (MAP_DISPLAY_WIDTH, MAP_DISPLAY_HEIGHT))
map_rect = map_img.get_rect()
player_img = load_image("KJK.png", PLAYER_SIZE)
devil_img = load_image("devil.png", ITEM_SIZE)
taxi_img = load_image("taxi.png", ITEM_SIZE)
subway_img = load_image("subway.png", ITEM_SIZE)
poop_img = load_image("poop.png", ITEM_SIZE)
edible_img = load_image("edible.png", ITEM_SIZE)
grenade_img = load_image("grenade.png", ITEM_SIZE)

start_screen_img = load_image("start_screen.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
win_screen_img = load_image("win_screen.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))
lose_screen_img = load_image("lose_screen.jpg", (SCREEN_WIDTH, SCREEN_HEIGHT))

hotspot_types = [
    {"name": "pretzel", "points": 4, "img": load_image("pretzel.png", ITEM_SIZE)},
    {"name": "dog", "points": 3, "img": load_image("dog.png", ITEM_SIZE)},
    {"name": "taxi", "points": 2, "img": taxi_img},
    {"name": "construction", "points": -3, "img": load_image("construction.png", ITEM_SIZE)},
    {"name": "rain", "points": -4, "img": load_image("rain.png", ITEM_SIZE)},
    {"name": "sun", "points": 0, "img": load_image("sun.png", ITEM_SIZE)},
    {"name": "subway", "points": 2, "img": subway_img},
    {"name": "edible", "points": 5, "img": edible_img},
    {"name": "pizza", "points": 5, "img": load_image("pizza.png", ITEM_SIZE)},
    {"name": "bagels", "points": 3, "img": load_image("bagels.png", ITEM_SIZE)},
    {"name": "tourist", "points": -4, "img": load_image("tourist.png", ITEM_SIZE)},
    {"name": "museum", "points": 5, "img": load_image("museum.png", ITEM_SIZE)},
    {"name": "coffee", "points": 5, "img": load_image("coffee.png", ITEM_SIZE)}
]

positive_sound = load_sound("positive.wav")
negative_sound = load_sound("negative.wav")
boom_sound = load_sound("boom.wav")

# === F: Game Loop ===
# === B: Game State ===
class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.player_rect = player_img.get_rect(center=map_rect.center)
        self.hotspots = []
        self.timed_events = []  # Store (timestamp, callback, event_id)
        self.next_event_id = 0
        self.devil = None
        self.sun_active = False
        self.sun_timer = 0
        self.edible_timers = []
        self.vibes = 10
        self.last_devil_spawn = 0
        self.devil_spawned_at = 0
        self.music_muted = False
        self.game_over = False
        self.result_text = ""
        self.inventory = []
        self.devil_disabled = False

    def apply_edible(self):
        self.edible_timers.append(pygame.time.get_ticks())

    def is_high(self):
        now = pygame.time.get_ticks()
        self.edible_timers = [t for t in self.edible_timers if now - t < EDIBLE_DURATION_MS]
        return len(self.edible_timers) > 0

    def schedule_event(self, delay_ms, callback, data=None):
        event_id = self.next_event_id
        self.timed_events.append((pygame.time.get_ticks() + delay_ms, callback, event_id, data))
        self.next_event_id += 1
        return event_id

    def cancel_event(self, event_id):
        self.timed_events = [event for event in self.timed_events if event[2] != event_id]

def spawn_poop(state, rect):
    state.hotspots.append({"name": "poop", "points": -5, "img": poop_img, "rect": rect})

# === F: Game Loop ===
def run_game():
    pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
    pygame.mixer.music.play(-1)

    show_start_screen()
    state = GameState()

    # Define the initial area around the player's start
    initial_spawn_radius = 200

    for item in ["coffee", "dog"]:
        spot = next(s for s in hotspot_types if s["name"] == item)
        # Generate random coordinates within the initial spawn radius
        random_x = random.randint(state.player_rect.centerx - initial_spawn_radius,
                                   state.player_rect.centerx + initial_spawn_radius - ITEM_SIZE[0])
        random_y = random.randint(state.player_rect.centery - initial_spawn_radius,
                                   state.player_rect.centery + initial_spawn_radius - ITEM_SIZE[1])

        # Ensure the coordinates are within the map bounds
        spawn_x = max(0, min(random_x, map_rect.width - ITEM_SIZE[0]))
        spawn_y = max(0, min(random_y, map_rect.height - ITEM_SIZE[1]))

        rect = spot["img"].get_rect(topleft=(spawn_x, spawn_y))
        state.hotspots.append({**spot, "rect": rect})
        if item == "dog":
            # Schedule the poop spawn and store the event ID
            dog_poop_event_id = state.schedule_event(DOG_TIMER_MS, spawn_poop, rect)
            # Store the event ID associated with this dog in the hotspot data
            for h in state.hotspots:
                if h['rect'] == rect and h['name'] == 'dog':
                    h['poop_event_id'] = dog_poop_event_id

    grenade_rect = grenade_img.get_rect(topleft=(random.randint(0, map_rect.width - ITEM_SIZE[0]), random.randint(0, map_rect.height - ITEM_SIZE[1])))
    state.hotspots.append({"name": "grenade", "points": 0, "img": grenade_img, "rect": grenade_rect})

    pygame.time.set_timer(USEREVENT+1, SPAWN_INTERVAL_MS)
    pygame.time.set_timer(USEREVENT+2, 4000)

    while not state.game_over:
        now = pygame.time.get_ticks()
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == USEREVENT+1:
                spot = random.choice(hotspot_types)
                rect = spot['img'].get_rect(topleft=(random.randint(0, map_rect.width - ITEM_SIZE[0]), random.randint(0, map_rect.height - ITEM_SIZE[1])))
                if spot['name'] == "dog":
                    state.hotspots.append({**spot, "rect": rect})
                    # Schedule poop for newly spawned dogs and store the event ID
                    dog_poop_event_id = state.schedule_event(DOG_TIMER_MS, spawn_poop, rect)
                    # Store the event ID associated with this dog
                    for h in state.hotspots:
                        if h['rect'] == rect and h['name'] == 'dog':
                            h['poop_event_id'] = dog_poop_event_id
                else:
                    state.hotspots.append({**spot, "rect": rect})
            elif event.type == USEREVENT+2 and not state.devil_disabled and state.devil is None:
                if now - state.last_devil_spawn > DEVIL_MIN_INTERVAL and random.random() < DEVIL_SPAWN_CHANCE:
                    state.devil = devil_img.get_rect(topleft=(random.randint(0, map_rect.width - ITEM_SIZE[0]), random.randint(0, map_rect.height - ITEM_SIZE[1])))
                    state.devil_spawned_at = now
                    state.last_devil_spawn = now
                    pygame.mixer.music.load(os.path.join("static", "dark.mp3"))
                    pygame.mixer.music.play(-1)

        keys = pygame.key.get_pressed()
        dx = (keys[K_RIGHT] - keys[K_LEFT]) * PLAYER_SPEED
        dy = (keys[K_DOWN] - keys[K_UP]) * PLAYER_SPEED
        state.player_rect.move_ip(dx, dy)
        state.player_rect.clamp_ip(map_rect)

        if state.devil:
            dx = DEVIL_SPEED if state.devil.x < state.player_rect.x else -DEVIL_SPEED
            dy = DEVIL_SPEED if state.devil.y < state.player_rect.y else -DEVIL_SPEED
            state.devil.move_ip(dx, dy)
            if state.player_rect.colliderect(state.devil):
                if "grenade" in state.inventory:
                    state.inventory.remove("grenade")
                    boom_sound.play()
                    flash = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
                    flash.fill((255, 255, 255))
                    flash.set_alpha(200)
                    screen.blit(flash, (0, 0))
                    pygame.display.flip()
                    pygame.time.delay(500)
                    state.devil = None
                    state.devil_disabled = True
                    pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
                    pygame.mixer.music.play(-1)
                else:
                    state.vibes -= 15
                    negative_sound.play()
                    state.devil = None
                    pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
                    pygame.mixer.music.play(-1)

            if now - state.devil_spawned_at > DEVIL_LIFESPAN:
                state.devil = None
                pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
                pygame.mixer.music.play(-1)

        # Process timed events
        new_timed_events = []
        for t, cb, event_id, data in state.timed_events:
            if now < t:
                new_timed_events.append((t, cb, event_id, data))
            else:
                cb(state, data)  # Execute the callback with state and data
        state.timed_events = new_timed_events

        camera_x = max(0, min(state.player_rect.centerx - SCREEN_WIDTH // 2, map_rect.width - SCREEN_WIDTH))
        camera_y = max(0, min(state.player_rect.centery - SCREEN_HEIGHT // 2, map_rect.height - SCREEN_HEIGHT))
        screen.blit(map_img, (-camera_x, -camera_y))

        for h in state.hotspots[:]:
            if state.player_rect.colliderect(h['rect']):
                if h['name'] == "grenade":
                    if "grenade" not in state.inventory:
                        state.inventory.append("grenade")
                    state.hotspots.remove(h)
                    continue
                pts = h['points'] * (2 if state.sun_active and h['points'] > 0 else 1)
                state.vibes += pts
                if pts > 0:
                    positive_sound.play()
                elif pts < 0:
                    negative_sound.play()

                if h['name'] == "sun":
                    state.sun_active = True
                    state.sun_timer = now
                elif h['name'] == "edible":
                    state.apply_edible()
                elif h['name'] == "museum":
                    if "map" not in state.inventory:
                        state.inventory.append("map")
                elif h['name'] in ["taxi", "subway"]:
                    if state.devil:
                        state.devil = None
                        pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
                        pygame.mixer.music.play(-1)
                elif h['name'] == "dog":
                    # When a dog is collected, cancel its poop event
                    if 'poop_event_id' in h:
                        state.cancel_event(h['poop_event_id'])

                state.hotspots.remove(h)
            else:
                screen.blit(h['img'], (h['rect'].x - camera_x, h['rect'].y - camera_y))

        if state.sun_active and now - state.sun_timer > SUN_DURATION_MS:
            state.sun_active = False

        screen.blit(player_img, (state.player_rect.x - camera_x, state.player_rect.y - camera_y))
        if state.devil:
            screen.blit(devil_img, (state.devil.x - camera_x, state.devil.y - camera_y))

        vibes_text = font.render(f"Vibes: {state.vibes}", True, WHITE, BLACK)
        screen.blit(vibes_text, (10, 10))

        inventory_text = font.render("Inventory: " + ", ".join(state.inventory), True, WHITE, BLACK)
        screen.blit(inventory_text, (SCREEN_WIDTH - inventory_text.get_width() - 10, 10))

        if state.sun_active:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(100)
            overlay.fill((255, 255, 180))
            screen.blit(overlay, (0, 0))
        if state.is_high():
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(90)
            r = random.randint(150, 255)
            g = random.randint(100, 255)
            b = random.randint(150, 255)
            overlay.fill((r, g, b))
            screen.blit(overlay, (0, 0))

        pygame.display.flip()

        if state.vibes >= 50:
            state.result_text = "win"
            state.game_over = True
        elif state.vibes <= 0:
            state.result_text = "lose"
            state.game_over = True

    screen.blit(win_screen_img if state.result_text == "win" else lose_screen_img, (0, 0))
    pygame.display.flip()
    wait_for_key()

# === G: Start ===
def show_start_screen():
    screen.blit(start_screen_img, (0, 0))
    pygame.display.flip()
    wait_for_key()
    pygame.mixer.music.load(os.path.join("static", "bg_music.mp3"))
    pygame.mixer.music.play(-1)

# Run Game
if __name__ == '__main__':
    run_game()




