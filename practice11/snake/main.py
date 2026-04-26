import pygame
import time
import random

pygame.init()
pygame.mixer.init()

coin_sound = pygame.mixer.Sound("coin.mp3")
window_x = 720
window_y = 480

snake_speed = 15
pygame.display.set_caption("Snake Game")
screen = pygame.display.set_mode((window_x, window_y))

black  = pygame.Color(0, 0, 0)
white  = pygame.Color(255, 255, 255)
red    = pygame.Color(255, 0, 0)
green  = pygame.Color(0, 255, 0)
yellow = pygame.Color(255, 215, 0)
orange = pygame.Color(255, 140, 0)
purple = pygame.Color(180, 0, 255)

fps = pygame.time.Clock()

# ── Food type definitions ─────────────────────────────────────────
# Each entry: (label, color, points, lifetime_ms, spawn_weight)
#   lifetime_ms = None  → food never disappears
#   spawn_weight controls how often this type is chosen
FOOD_TYPES = [
    ("common", white,  1, None, 50),   # plain – always present
    ("bonus",  yellow, 3, 5000, 30),   # 5 s timer, worth 3
    ("rare",   orange, 5, 3000, 15),   # 3 s timer, worth 5
    ("epic",   purple, 8, 2000, 5),    # 2 s timer, worth 8
]

snake_position = [100, 50]
snake_body     = [[100, 50], [90, 50], [80, 50], [70, 50]]
direction      = "RIGHT"
change_to      = direction
score          = 0


# ── Food helpers ──────────────────────────────────────────────────

def random_position():
    """Return a grid-aligned (x, y) that does not land on the snake body."""
    while True:
        pos = [
            random.randrange(1, window_x // 10) * 10,
            random.randrange(1, window_y // 10) * 10,
        ]
        if pos not in snake_body:
            return pos

def pick_food_type():
    labels  = [f[0] for f in FOOD_TYPES]
    weights = [f[4] for f in FOOD_TYPES]
    return random.choices(FOOD_TYPES, weights=weights, k=1)[0]

def spawn_food():
    """Return a food dict with position, type info, and a spawn timestamp."""
    ftype = pick_food_type()
    label, color, points, lifetime_ms, _ = ftype
    return {
        "pos":         random_position(),
        "color":       color,
        "points":      points,
        "lifetime_ms": lifetime_ms,
        "spawned_at":  pygame.time.get_ticks(),
        "label":       label,
    }

# Start with one food item on the board
active_foods = [spawn_food()]
MAX_FOODS = 3   # How many food items can coexist at once


# ── HUD helpers ───────────────────────────────────────────────────

def show_score():
    font    = pygame.font.SysFont("times new roman", 20)
    surface = font.render("Score: " + str(score), True, white)
    rect    = surface.get_rect(midtop=(window_x // 2, 10))
    screen.blit(surface, rect)

def show_food_legend():
    """Small legend in the top-left corner."""
    font = pygame.font.SysFont("times new roman", 14)
    for i, (label, color, pts, lifetime, _) in enumerate(FOOD_TYPES):
        timer_str = f"{lifetime//1000}s" if lifetime else "∞"
        text = f"{label}: +{pts} ({timer_str})"
        surf = font.render(text, True, color)
        screen.blit(surf, (8, 8 + i * 18))

def draw_food_timers(foods):
    """Draw a shrinking arc/bar around timed food items."""
    for food in foods:
        if food["lifetime_ms"] is None:
            continue
        elapsed   = pygame.time.get_ticks() - food["spawned_at"]
        remaining = food["lifetime_ms"] - elapsed
        ratio     = max(0, remaining / food["lifetime_ms"])

        # Colour shifts red as time runs out
        r = int(255 * (1 - ratio))
        g = int(200 * ratio)
        bar_color = pygame.Color(r, g, 0)

        fx, fy = food["pos"]
        bar_w  = int(20 * ratio)   # shrinks left-to-right
        pygame.draw.rect(screen, bar_color,
                         pygame.Rect(fx - 5, fy - 6, bar_w, 3))

def game_over():
    my_font  = pygame.font.SysFont("times new roman", 50)
    surface  = my_font.render("Your Score is: " + str(score), True, red)
    rect     = surface.get_rect(midtop=(window_x / 2, window_y / 4))
    screen.blit(surface, rect)
    pygame.display.flip()
    time.sleep(1)
    pygame.quit()
    quit()


# ── Main loop ─────────────────────────────────────────────────────

FOOD_SPAWN_INTERVAL = 3000   # ms between automatic new food spawns
last_spawn_time     = pygame.time.get_ticks()

while True:
    now = pygame.time.get_ticks()

    # ── Input ──
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:    change_to = "UP"
            if event.key == pygame.K_DOWN:  change_to = "DOWN"
            if event.key == pygame.K_LEFT:  change_to = "LEFT"
            if event.key == pygame.K_RIGHT: change_to = "RIGHT"

    if change_to == "UP"    and direction != "DOWN":  direction = "UP"
    if change_to == "DOWN"  and direction != "UP":    direction = "DOWN"
    if change_to == "LEFT"  and direction != "RIGHT": direction = "LEFT"
    if change_to == "RIGHT" and direction != "LEFT":  direction = "RIGHT"

    # ── Move snake ──
    if direction == "UP":    snake_position[1] -= 10
    if direction == "DOWN":  snake_position[1] += 10
    if direction == "LEFT":  snake_position[0] -= 10
    if direction == "RIGHT": snake_position[0] += 10

    # ── Expire timed foods ──
    active_foods = [
        f for f in active_foods
        if f["lifetime_ms"] is None
        or (now - f["spawned_at"]) < f["lifetime_ms"]
    ]

    # ── Spawn new food periodically (up to MAX_FOODS) ──
    if now - last_spawn_time >= FOOD_SPAWN_INTERVAL and len(active_foods) < MAX_FOODS:
        active_foods.append(spawn_food())
        last_spawn_time = now

    # Always ensure at least one food exists
    if not active_foods:
        active_foods.append(spawn_food())
        last_spawn_time = now

    # ── Grow / eat ──
    snake_body.insert(0, list(snake_position))
    ate = False
    for food in active_foods[:]:          # iterate a copy
        if snake_position == food["pos"]:
            score += food["points"]
            active_foods.remove(food)
            coin_sound.set_volume(0.5)
            coin_sound.play()
            ate = True
            break

    if not ate:
        snake_body.pop()

    # ── Draw ──
    screen.fill(black)


    # Snake
    for pos in snake_body:
        pygame.draw.rect(screen, green,
                         pygame.Rect(pos[0], pos[1], 10, 10))

    # Food items
    for food in active_foods:
        fx, fy = food["pos"]
        pygame.draw.rect(screen, food["color"],
                         pygame.Rect(fx, fy, 10, 10))

    draw_food_timers(active_foods)
    show_score()

    # ── Game-over checks ──
    if snake_position[0] < 0 or snake_position[0] > window_x - 10:
        game_over()
    if snake_position[1] < 0 or snake_position[1] > window_y - 10:
        game_over()
    for block in snake_body[1:]:
        if snake_position == block:
            game_over()

    pygame.display.update()
    fps.tick(snake_speed)   