# game.py — Core Snake game logic (rendering, input, physics)

import random
import pygame
from config import (
    WINDOW_X, WINDOW_Y, GRID_SIZE,
    DEFAULT_SNAKE_SPEED, SPEED_INCREMENT,
    FOOD_TYPES, MAX_FOODS, FOOD_SPAWN_INTERVAL,
    POWERUP_TYPES, POWERUP_SPAWN_INTERVAL, POWERUP_EFFECT_DURATION,
    POISON_SHORTEN, MIN_SNAKE_LENGTH,
    OBSTACLE_START_LEVEL, OBSTACLES_PER_LEVEL,
    SCORE_PER_LEVEL,
)

# ── Colours ───────────────────────────────────────────────────────

BLACK  = pygame.Color(0,   0,   0)
WHITE  = pygame.Color(255, 255, 255)
RED    = pygame.Color(255,   0,   0)
GREEN  = pygame.Color(0,   255,   0)
DARK_GREEN = pygame.Color(0, 180, 0)


# ── Helpers ───────────────────────────────────────────────────────

def _random_pos(blocked: list[list]) -> list:
    """Return a grid-aligned position not in *blocked*."""
    while True:
        pos = [
            random.randrange(1, WINDOW_X // GRID_SIZE) * GRID_SIZE,
            random.randrange(1, WINDOW_Y // GRID_SIZE) * GRID_SIZE,
        ]
        if pos not in blocked:
            return pos


def _pick_food_type():
    weights = [f[4] for f in FOOD_TYPES]
    return random.choices(FOOD_TYPES, weights=weights, k=1)[0]


def _spawn_food(blocked):
    label, color_rgb, points, lifetime_ms, _ = _pick_food_type()
    return {
        "pos":         _random_pos(blocked),
        "color":       pygame.Color(*color_rgb),
        "points":      points,
        "lifetime_ms": lifetime_ms,
        "spawned_at":  pygame.time.get_ticks(),
        "label":       label,
        "is_poison":   label == "poison",
    }


def _spawn_powerup(blocked):
    ptype = random.choice(POWERUP_TYPES)
    label, color_rgb, field_lifetime = ptype
    return {
        "pos":          _random_pos(blocked),
        "color":        pygame.Color(*color_rgb),
        "label":        label,
        "field_life":   field_lifetime,
        "spawned_at":   pygame.time.get_ticks(),
    }


def _level_from_score(score: int) -> int:
    return score // SCORE_PER_LEVEL + 1


def _generate_obstacles(level: int, snake_body: list, food_positions: list) -> list:
    """Return a list of [x, y] obstacle blocks for the given level."""
    if level < OBSTACLE_START_LEVEL:
        return []
    count = (level - OBSTACLE_START_LEVEL + 1) * OBSTACLES_PER_LEVEL
    blocked = list(snake_body) + list(food_positions)
    obstacles = []
    attempts = 0
    while len(obstacles) < count and attempts < 500:
        attempts += 1
        pos = [
            random.randrange(2, WINDOW_X // GRID_SIZE - 2) * GRID_SIZE,
            random.randrange(2, WINDOW_Y // GRID_SIZE - 2) * GRID_SIZE,
        ]
        if pos not in blocked and pos not in obstacles:
            obstacles.append(pos)
            blocked.append(pos)
    return obstacles


# ── GameSession ───────────────────────────────────────────────────

class GameSession:
    """Encapsulates one run of the snake game."""

    def __init__(self, screen: pygame.Surface, settings: dict,
                 coin_sound, personal_best: int):
        self.screen       = screen
        self.settings     = settings
        self.coin_sound   = coin_sound
        self.personal_best = personal_best

        # Snake state
        self.snake_pos  = [100, 50]
        self.snake_body = [[100, 50], [90, 50], [80, 50], [70, 50]]
        self.direction  = "RIGHT"
        self.change_to  = "RIGHT"

        # Score / level
        self.score        = 0
        self.level        = 1
        self.snake_speed  = DEFAULT_SNAKE_SPEED

        # Food
        self.active_foods    = [_spawn_food(self.snake_body)]
        self.last_food_spawn = pygame.time.get_ticks()

        # Power-ups
        self.field_powerup      = None   # powerup lying on the field
        self.active_powerup     = None   # collected powerup currently in effect
        self.powerup_effect_end = 0
        self.last_powerup_spawn = pygame.time.get_ticks()
        self.shield_active      = False

        # Obstacles
        self.obstacles = []

        # Fonts
        self.font_sm  = pygame.font.SysFont("consolas", 16)
        self.font_med = pygame.font.SysFont("consolas", 22)
        self.font_lg  = pygame.font.SysFont("consolas", 50)

        self.clock = pygame.time.Clock()

    # ── Internal helpers ──────────────────────────────────────────

    def _all_blocked(self):
        return (
            self.snake_body
            + [f["pos"] for f in self.active_foods]
            + self.obstacles
            + ([self.field_powerup["pos"]] if self.field_powerup else [])
        )

    def _update_level(self):
        new_level = _level_from_score(self.score)
        if new_level > self.level:
            self.level = new_level
            self.snake_speed = DEFAULT_SNAKE_SPEED + (self.level - 1) * SPEED_INCREMENT
            # Regenerate obstacles for the new level
            self.obstacles = _generate_obstacles(
                self.level, self.snake_body,
                [f["pos"] for f in self.active_foods]
            )

    def _apply_powerup(self, label):
        self.active_powerup     = label
        self.powerup_effect_end = pygame.time.get_ticks() + POWERUP_EFFECT_DURATION
        if label == "speed_boost":
            self.snake_speed = DEFAULT_SNAKE_SPEED + (self.level - 1) * SPEED_INCREMENT + 8
        elif label == "slow_motion":
            base = DEFAULT_SNAKE_SPEED + (self.level - 1) * SPEED_INCREMENT
            self.snake_speed = max(4, base - 6)
        elif label == "shield":
            self.shield_active = True

    def _expire_powerup(self):
        if self.active_powerup and pygame.time.get_ticks() >= self.powerup_effect_end:
            if self.active_powerup in ("speed_boost", "slow_motion"):
                self.snake_speed = DEFAULT_SNAKE_SPEED + (self.level - 1) * SPEED_INCREMENT
            self.active_powerup = None
            self.shield_active  = False

    # ── Drawing helpers ───────────────────────────────────────────

    def _draw_grid(self):
        for x in range(0, WINDOW_X, GRID_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), (x, 0), (x, WINDOW_Y))
        for y in range(0, WINDOW_Y, GRID_SIZE):
            pygame.draw.line(self.screen, (20, 20, 20), (0, y), (WINDOW_X, y))

    def _draw_snake(self):
        snake_color = pygame.Color(*self.settings.get("snake_color", (0, 255, 0)))
        for i, pos in enumerate(self.snake_body):
            shade = snake_color if i > 0 else DARK_GREEN
            pygame.draw.rect(self.screen, shade,
                             pygame.Rect(pos[0], pos[1], GRID_SIZE, GRID_SIZE))

    def _draw_foods(self):
        now = pygame.time.get_ticks()
        for food in self.active_foods:
            fx, fy = food["pos"]
            pygame.draw.rect(self.screen, food["color"],
                             pygame.Rect(fx, fy, GRID_SIZE, GRID_SIZE))
            if food["lifetime_ms"]:
                elapsed   = now - food["spawned_at"]
                ratio     = max(0, 1 - elapsed / food["lifetime_ms"])
                r = int(255 * (1 - ratio))
                g = int(200 * ratio)
                bar_w = int(20 * ratio)
                pygame.draw.rect(self.screen, pygame.Color(r, g, 0),
                                 pygame.Rect(fx - 5, fy - 6, bar_w, 3))

    def _draw_powerup(self):
        if not self.field_powerup:
            return
        now     = pygame.time.get_ticks()
        elapsed = now - self.field_powerup["spawned_at"]
        ratio   = max(0, 1 - elapsed / self.field_powerup["field_life"])
        fx, fy  = self.field_powerup["pos"]
        pygame.draw.rect(self.screen, self.field_powerup["color"],
                         pygame.Rect(fx, fy, GRID_SIZE, GRID_SIZE))
        # Diamond shape overlay
        cx, cy = fx + GRID_SIZE // 2, fy + GRID_SIZE // 2
        pygame.draw.polygon(self.screen, WHITE, [
            (cx, fy - 2), (fx + GRID_SIZE + 2, cy),
            (cx, fy + GRID_SIZE + 2), (fx - 2, cy)
        ], 1)
        # Timer bar
        pygame.draw.rect(self.screen, self.field_powerup["color"],
                         pygame.Rect(fx - 5, fy - 6, int(20 * ratio), 3))

    def _draw_obstacles(self):
        for obs in self.obstacles:
            pygame.draw.rect(self.screen, pygame.Color(100, 100, 100),
                             pygame.Rect(obs[0], obs[1], GRID_SIZE, GRID_SIZE))

    def _draw_hud(self):
        # Score + level
        score_surf = self.font_med.render(
            f"Score: {self.score}  Lvl: {self.level}", True, WHITE)
        self.screen.blit(score_surf, score_surf.get_rect(midtop=(WINDOW_X // 2, 6)))

        # Personal best
        pb_surf = self.font_sm.render(f"Best: {self.personal_best}", True, (180, 180, 180))
        self.screen.blit(pb_surf, (WINDOW_X - pb_surf.get_width() - 8, 8))

        # Active power-up
        if self.active_powerup:
            remaining = max(0, self.powerup_effect_end - pygame.time.get_ticks())
            pu_surf = self.font_sm.render(
                f"⚡ {self.active_powerup}  {remaining//1000+1}s", True, (255, 255, 0))
            self.screen.blit(pu_surf, (8, WINDOW_Y - 24))

        # Shield indicator
        if self.shield_active:
            sh_surf = self.font_sm.render("🛡 Shield", True, (255, 255, 0))
            self.screen.blit(sh_surf, (8, WINDOW_Y - 44))

        # Food legend (top-left)
        for i, (label, color_rgb, pts, lifetime, _) in enumerate(FOOD_TYPES):
            t = f"{label}: +{pts} ({lifetime//1000}s)" if lifetime else f"{label}: +{pts}"
            s = self.font_sm.render(t, True, pygame.Color(*color_rgb))
            self.screen.blit(s, (8, 8 + i * 16))

    # ── Main run loop ─────────────────────────────────────────────

    def run(self) -> dict:
        """
        Run the game until the player dies.
        Returns {"score": int, "level": int}.
        """
        while True:
            now = pygame.time.get_ticks()

            # ── Input ──────────────────────────────────────────────
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    raise SystemExit
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:    self.change_to = "UP"
                    if event.key == pygame.K_DOWN:  self.change_to = "DOWN"
                    if event.key == pygame.K_LEFT:  self.change_to = "LEFT"
                    if event.key == pygame.K_RIGHT: self.change_to = "RIGHT"

            if self.change_to == "UP"    and self.direction != "DOWN":  self.direction = "UP"
            if self.change_to == "DOWN"  and self.direction != "UP":    self.direction = "DOWN"
            if self.change_to == "LEFT"  and self.direction != "RIGHT": self.direction = "LEFT"
            if self.change_to == "RIGHT" and self.direction != "LEFT":  self.direction = "RIGHT"

            # ── Move ───────────────────────────────────────────────
            if self.direction == "UP":    self.snake_pos[1] -= GRID_SIZE
            if self.direction == "DOWN":  self.snake_pos[1] += GRID_SIZE
            if self.direction == "LEFT":  self.snake_pos[0] -= GRID_SIZE
            if self.direction == "RIGHT": self.snake_pos[0] += GRID_SIZE

            # ── Expire timed foods ─────────────────────────────────
            self.active_foods = [
                f for f in self.active_foods
                if f["lifetime_ms"] is None
                or (now - f["spawned_at"]) < f["lifetime_ms"]
            ]

            # ── Spawn food ─────────────────────────────────────────
            if (now - self.last_food_spawn >= FOOD_SPAWN_INTERVAL
                    and len(self.active_foods) < MAX_FOODS):
                self.active_foods.append(_spawn_food(self._all_blocked()))
                self.last_food_spawn = now
            if not self.active_foods:
                self.active_foods.append(_spawn_food(self._all_blocked()))
                self.last_food_spawn = now

            # ── Spawn power-up ─────────────────────────────────────
            if (self.field_powerup is None
                    and now - self.last_powerup_spawn >= POWERUP_SPAWN_INTERVAL):
                self.field_powerup     = _spawn_powerup(self._all_blocked())
                self.last_powerup_spawn = now

            # Expire field power-up
            if self.field_powerup:
                age = now - self.field_powerup["spawned_at"]
                if age >= self.field_powerup["field_life"]:
                    self.field_powerup      = None
                    self.last_powerup_spawn = now

            # ── Expire active power-up ─────────────────────────────
            self._expire_powerup()

            # ── Grow / eat ─────────────────────────────────────────
            self.snake_body.insert(0, list(self.snake_pos))
            ate = False
            dead = False

            for food in self.active_foods[:]:
                if self.snake_pos == food["pos"]:
                    if food["is_poison"]:
                        # Shorten snake
                        for _ in range(POISON_SHORTEN):
                            if len(self.snake_body) > 1:
                                self.snake_body.pop()
                        if len(self.snake_body) <= MIN_SNAKE_LENGTH:
                            dead = True
                    else:
                        self.score += food["points"]
                        if self.settings.get("sound", True) and self.coin_sound:
                            self.coin_sound.set_volume(0.5)
                            self.coin_sound.play()
                    self.active_foods.remove(food)
                    ate = True
                    break

            if not ate:
                self.snake_body.pop()

            # Check power-up pickup
            if self.field_powerup and self.snake_pos == self.field_powerup["pos"]:
                self._apply_powerup(self.field_powerup["label"])
                self.field_powerup      = None
                self.last_powerup_spawn = now

            self._update_level()

            # ── Collision detection ────────────────────────────────
            oob = (
                self.snake_pos[0] < 0 or self.snake_pos[0] > WINDOW_X - GRID_SIZE
                or self.snake_pos[1] < 0 or self.snake_pos[1] > WINDOW_Y - GRID_SIZE
            )
            self_collision = self.snake_pos in self.snake_body[1:]
            obs_collision  = self.snake_pos in self.obstacles

            if oob or self_collision or obs_collision:
                if self.shield_active:
                    # Shield absorbs one hit — reposition snake to a safe spot
                    self.shield_active = False
                    self.active_powerup = None
                    safe = _random_pos(self._all_blocked())
                    self.snake_pos = safe
                    self.snake_body[0] = list(safe)
                    self.direction = "RIGHT"
                    self.change_to = "RIGHT"
                else:
                    dead = True

            if dead:
                return {"score": self.score, "level": self.level}

            # ── Draw ───────────────────────────────────────────────
            self.screen.fill(BLACK)
            if self.settings.get("grid", False):
                self._draw_grid()
            self._draw_obstacles()
            self._draw_foods()
            self._draw_powerup()
            self._draw_snake()
            self._draw_hud()

            pygame.display.update()
            self.clock.tick(self.snake_speed)
