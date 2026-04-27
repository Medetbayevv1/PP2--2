# config.py — Central constants for the Snake game

WINDOW_X = 720
WINDOW_Y = 480
GRID_SIZE = 10

DEFAULT_SNAKE_SPEED = 15
CAPTION = "Snake Game"

# Food type definitions: (label, color_rgb, points, lifetime_ms, spawn_weight)
FOOD_TYPES = [
    ("common", (255, 255, 255), 1, None,  50),
    ("bonus",  (255, 215,   0), 3, 5000,  30),
    ("rare",   (255, 140,   0), 5, 3000,  15),
    ("epic",   (180,   0, 255), 8, 2000,   5),
    ("poison", (139,   0,   0), 0, 6000,  10),   # poison — shrinks snake
]

MAX_FOODS = 3
FOOD_SPAWN_INTERVAL = 3000   # ms

# Power-up definitions: (label, color_rgb, field_lifetime_ms)
POWERUP_TYPES = [
    ("speed_boost", (0, 255, 200), 8000),
    ("slow_motion", (0, 150, 255), 8000),
    ("shield",      (255, 255,  0), 8000),
]
POWERUP_SPAWN_INTERVAL = 10_000   # ms between power-up spawns
POWERUP_EFFECT_DURATION = 5000    # ms effect lasts after collection

POISON_SHORTEN = 2       # segments removed when snake eats poison
MIN_SNAKE_LENGTH = 1     # game over if length drops to this or below after poison

# Obstacles: start appearing from this level
OBSTACLE_START_LEVEL = 3
OBSTACLES_PER_LEVEL  = 5   # extra blocks added each level (above 3)

# Level progression
SCORE_PER_LEVEL = 10   # score thresholds: level = score // SCORE_PER_LEVEL + 1
SPEED_INCREMENT = 2    # extra snake speed per level above 1
