import pygame, sys, random, time
from pygame.locals import *

# ── colours ───────────────────────────────────────────────────────────────────
BLACK   = (0,   0,   0)
WHITE   = (255, 255, 255)
RED     = (220, 50,  50)
GREEN   = (50,  200, 80)
GOLD    = (255, 215, 0)
SILVER  = (192, 192, 192)
BRONZE  = (205, 127, 50)
BLUE    = (30,  120, 220)
CYAN    = (0,   220, 255)
ORANGE  = (255, 140, 0)
PURPLE  = (160, 50,  200)
GRAY    = (130, 130, 130)
DARK    = (20,  20,  30)
OIL_CLR = (30,  30,  50)
SLOW_CLR= (200, 200, 50)
NITRO_CLR=(50,  220, 255)
BUMP_CLR= (120, 90,  50)

SCREEN_WIDTH  = 400
SCREEN_HEIGHT = 600

# coin types: (label, fill, border, radius, points, weight)
COIN_TYPES = [
    ("bronze", BRONZE, (160, 90, 30),   7, 1, 55),
    ("silver", SILVER, (140,140,140),   8, 2, 30),
    ("gold",   GOLD,   (200,160,  0),   9, 3, 15),
]

# difficulty presets
DIFF = {
    "easy":   {"speed": 2.5, "inc": 0.12, "spawn_ms": 1800, "enemies": 1, "obs_ms": 4000},
    "normal": {"speed": 3.0, "inc": 0.20, "spawn_ms": 1500, "enemies": 1, "obs_ms": 3000},
    "hard":   {"speed": 4.0, "inc": 0.30, "spawn_ms": 1100, "enemies": 2, "obs_ms": 2000},
}


# ── Sprite helpers ────────────────────────────────────────────────────────────

class Coin(pygame.sprite.Sprite):
    def __init__(self, enemies_group, speed_ref):
        super().__init__()
        self._speed = speed_ref
        chosen = random.choices(COIN_TYPES, weights=[c[5] for c in COIN_TYPES], k=1)[0]
        _, color, border_color, radius, self.points, _ = chosen
        size = radius * 2 + 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        cx = size // 2
        pygame.draw.circle(self.image, color, (cx, cx), radius)
        pygame.draw.circle(self.image, border_color, (cx, cx), radius, 2)
        cf = pygame.font.SysFont("Verdana", max(8, radius - 2), bold=True)
        lbl = cf.render(str(self.points), True, border_color)
        self.image.blit(lbl, lbl.get_rect(center=(cx, cx)))
        self.rect = self.image.get_rect()
        for _ in range(20):
            self.rect.center = (random.randint(20, SCREEN_WIDTH - 20), -20)
            if not pygame.sprite.spritecollideany(self, enemies_group):
                break

    def move(self):
        self.rect.move_ip(0, self._speed[0])
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


ASSETS = "assets/"

class Enemy(pygame.sprite.Sprite):
    def __init__(self, speed_ref, score_ref):
        super().__init__()
        self._speed     = speed_ref
        self._score_ref = score_ref
        self.image = pygame.image.load(ASSETS + "Enemy.png")
        self.rect  = self.image.get_rect()
        self._reset()

    def _reset(self):
        self.rect.center = (random.randint(40, SCREEN_WIDTH - 40), -self.rect.height)

    def move(self):
        self.rect.move_ip(0, self._speed[0])
        if self.rect.top > SCREEN_HEIGHT:
            self._score_ref[0] += 1
            self._reset()


class Player(pygame.sprite.Sprite):
    def __init__(self, car_color="blue"):
        super().__init__()
        fname = ASSETS + ("Player.png" if car_color == "blue" else "Enemy.png")
        try:
            self.image = pygame.image.load(fname)
        except Exception:
            self.image = pygame.Surface((40, 70))
            self.image.fill((0, 100, 255))
        self.rect  = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, 520)
        self.shielded = False

    def move(self):
        keys = pygame.key.get_pressed()
        if self.rect.left > 0 and keys[K_LEFT]:
            self.rect.move_ip(-5, 0)
        if self.rect.right < SCREEN_WIDTH and keys[K_RIGHT]:
            self.rect.move_ip(5, 0)


# ── Road hazards ──────────────────────────────────────────────────────────────

class OilSpill(pygame.sprite.Sprite):
    def __init__(self, speed_ref, on_exit=None):
        super().__init__()
        self._speed    = speed_ref
        self._on_exit  = on_exit   # called when sprite scrolls off screen
        w, h = random.randint(50, 90), random.randint(25, 40)
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (*OIL_CLR, 200), (0, 0, w, h))
        self.rect = self.image.get_rect()
        self.rect.topleft = (random.randint(10, SCREEN_WIDTH - w - 10), -h)

    def move(self):
        self.rect.move_ip(0, self._speed[0])
        if self.rect.top > SCREEN_HEIGHT:
            if self._on_exit:
                self._on_exit()
            self.kill()


class SpeedBump(pygame.sprite.Sprite):
    def __init__(self, speed_ref):
        super().__init__()
        self._speed = speed_ref
        w = SCREEN_WIDTH - 60
        h = 14
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        # striped bump
        for i in range(0, w, 20):
            col = (255, 220, 0) if (i // 20) % 2 == 0 else (50, 50, 50)
            pygame.draw.rect(self.image, col, (i, 0, 20, h))
        self.rect = self.image.get_rect()
        self.rect.center = (SCREEN_WIDTH // 2, -h)

    def move(self):
        self.rect.move_ip(0, self._speed[0])
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()


class RoadObstacle(pygame.sprite.Sprite):
    SHAPES = ["rock", "cone"]

    def __init__(self, speed_ref):
        super().__init__()
        self._speed = speed_ref
        kind = random.choice(self.SHAPES)
        if kind == "rock":
            w, h = 22, 18
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)

            pygame.draw.ellipse(self.image, (110, 110, 110), (0, 4, w, h - 4))
            pygame.draw.ellipse(self.image, (90, 90, 90),    (3, 0, w - 8, h - 6))
            pygame.draw.ellipse(self.image, (150, 150, 150), (4, 2, 8, 6))  
        else:  # cone
            w, h = 18, 24
            self.image = pygame.Surface((w, h), pygame.SRCALPHA)
            # orange traffic cone
            points = [(w // 2, 0), (0, h), (w, h)]
            pygame.draw.polygon(self.image, (255, 100, 0), points)
            pygame.draw.polygon(self.image, (255, 200, 0), points, 2)
            pygame.draw.rect(self.image, (255, 255, 255), (3, h - 8, w - 6, 4))

        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(20, SCREEN_WIDTH - 20), -h)

    def move(self):
        self.rect.move_ip(0, self._speed[0])
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()



class PowerUp(pygame.sprite.Sprite):
    TYPES = {
        "nitro":  (CYAN,   "NITRO"),
        "shield": (PURPLE, "SHIELD"),
        "repair": (GREEN,  "REPAIR"),
    }
    TIMEOUT = 8000   

    def __init__(self, speed_ref):
        super().__init__()
        self._speed   = speed_ref
        self.kind     = random.choice(list(self.TYPES.keys()))
        color, label  = self.TYPES[self.kind]
        w, h = 68, 30
        self.image = pygame.Surface((w, h), pygame.SRCALPHA)
        pygame.draw.rect(self.image, (*color, 230), (0, 0, w, h), border_radius=8)
        pygame.draw.rect(self.image, WHITE, (0, 0, w, h), 2, border_radius=8)
        fnt = pygame.font.SysFont("Verdana", 10, bold=True)
        lbl = fnt.render(label, True, DARK)
        self.image.blit(lbl, lbl.get_rect(center=(w//2, h//2)))
        self.rect = self.image.get_rect()
        self.rect.center = (random.randint(40, SCREEN_WIDTH-40), -h)
        self._born = pygame.time.get_ticks()

    def move(self):
        self.rect.move_ip(0, self._speed[0])
        if self.rect.top > SCREEN_HEIGHT:
            self.kill()
        if pygame.time.get_ticks() - self._born > self.TIMEOUT:
            self.kill()




class ScrollBG:
    def __init__(self, image, speed_ref):
        self._img   = image
        self._speed = speed_ref
        self._y1    = 0
        self._y2    = -image.get_height()

    def update_and_draw(self, surf):
        self._y1 += self._speed[0]
        self._y2 += self._speed[0]
        h = self._img.get_height()
        if self._y1 >= SCREEN_HEIGHT:
            self._y1 = self._y2 - h
        if self._y2 >= SCREEN_HEIGHT:
            self._y2 = self._y1 - h
        surf.blit(self._img, (0, int(self._y1)))
        surf.blit(self._img, (0, int(self._y2)))




class GameSession:
    NITRO_DUR  = 4000
    SHIELD_DUR = 999999   

    def __init__(self, surf, settings):
        self.surf     = surf
        self.settings = settings
        self.W, self.H = surf.get_size()

        diff_key  = settings.get("difficulty", "normal")
        self.diff = DIFF[diff_key]

        # mutable speed/score containers (so sprites share reference)
        self._speed     = [self.diff["speed"]]
        self._score     = [0]

        # game state
        self.coin_points      = 0
        self.coin_milestone   = 10
        self.last_milestone   = 0
        self.speed_flash      = 0        # frames

        self.distance         = 0        # metres (approximate)
        self.distance_timer   = 0        # pixel accumulator

        self.active_powerup   = None     # "nitro" | "shield" | "repair" | None
        self.powerup_end      = 0        # ticks
        self._base_speed      = self.diff["speed"]
        self._nitro_boost     = 3.0

        self.on_oil           = False    # True while player overlaps oil
        self._oil_applied     = False    # True while the speed reduction is active
        self._OIL_SLOW        = 1.5      # fixed speed units removed while on oil
        self.shield_active    = False

        self.alive            = True
        self.result           = None

        # sounds
        try:
            self.coin_sound  = pygame.mixer.Sound(ASSETS + "collsound.mp3")
            self.crash_sound = pygame.mixer.Sound(ASSETS + "crash.wav")
        except Exception:
            self.coin_sound  = None
            self.crash_sound = None

        self.sound_on = settings.get("sound", True)

        # background music
        if self.sound_on:
            try:
                pygame.mixer.music.load(ASSETS + "background.wav")
                pygame.mixer.music.play(-1)
            except Exception:
                pass

        # background
        try:
            bg_img = pygame.image.load(ASSETS + "AnimatedStreet.png")
            bg_img = pygame.transform.scale(bg_img, (SCREEN_WIDTH, SCREEN_HEIGHT))
        except Exception:
            bg_img = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            bg_img.fill((80, 80, 80))
        self.bg = ScrollBG(bg_img, self._speed)

        # player
        self.player = Player(settings.get("car_color", "blue"))

        # sprite groups
        self.enemies     = pygame.sprite.Group()
        self.coins       = pygame.sprite.Group()
        self.oils        = pygame.sprite.Group()   # OilSpill only
        self.bumps       = pygame.sprite.Group()   # SpeedBump only
        self.obstacles   = pygame.sprite.Group()   # RoadObstacle (kills player)
        self.powerups    = pygame.sprite.Group()   # collectible power-ups
        self.all_sprites = pygame.sprite.Group()

        for _ in range(self.diff["enemies"]):
            e = Enemy(self._speed, self._score)
            self.enemies.add(e)
            self.all_sprites.add(e)

        self.all_sprites.add(self.player)

        # timers
        self.INC_SPEED      = pygame.USEREVENT + 1
        self.SPAWN_COIN     = pygame.USEREVENT + 2
        self.SPAWN_OBS      = pygame.USEREVENT + 3
        self.SPAWN_PU       = pygame.USEREVENT + 4
        self.SPAWN_EVENT    = pygame.USEREVENT + 5
        self.SPAWN_OBSTACLE = pygame.USEREVENT + 6

        pygame.time.set_timer(self.INC_SPEED,      1000)
        pygame.time.set_timer(self.SPAWN_COIN,      self.diff["spawn_ms"])
        pygame.time.set_timer(self.SPAWN_OBS,       self.diff["obs_ms"])
        pygame.time.set_timer(self.SPAWN_PU,        6000)
        pygame.time.set_timer(self.SPAWN_EVENT,     5000)
        pygame.time.set_timer(self.SPAWN_OBSTACLE,  2500)
        # fonts
        self.f_small  = pygame.font.SysFont("Verdana", 18, bold=True)
        self.f_flash  = pygame.font.SysFont("Verdana", 26, bold=True)
        self.f_gameover = pygame.font.SysFont("Verdana", 52, bold=True)
        self.f_pu     = pygame.font.SysFont("Verdana", 15, bold=True)

    # ── helpers ──────────────────────────────────────────────────────────────

    def _oil_scroll_away(self):
        if self._oil_applied:
            self._oil_applied = False
            self.on_oil       = False
            self._speed[0]    = min(self._speed[0] + self._OIL_SLOW, 10)

    def _play(self, sound):
        if self.sound_on and sound:
            sound.play()

    def _stop_timers(self):
        for ev in [self.INC_SPEED, self.SPAWN_COIN, self.SPAWN_OBS,
                   self.SPAWN_PU, self.SPAWN_EVENT, self.SPAWN_OBSTACLE]:
            pygame.time.set_timer(ev, 0)
    def _apply_powerup(self, kind):
        now = pygame.time.get_ticks()
        if kind == "nitro":
            self.active_powerup = "nitro"
            self.powerup_end    = now + self.NITRO_DUR
            self._speed[0]      = min(self._speed[0] + self._nitro_boost, 14)
        elif kind == "shield":
            self.active_powerup = "shield"
            self.shield_active  = True
            self.powerup_end    = now + self.SHIELD_DUR
            self.player.shielded = True
        elif kind == "repair":
            for h in list(self.oils.sprites()):
                h.kill()
            for h in list(self.bumps.sprites()):
                h.kill()
            if self._oil_applied:
                self._speed[0] = min(self._speed[0] + self._OIL_SLOW, 10)
                self._oil_applied = False
            self.on_oil         = False
            self.active_powerup = None

    def _expire_powerup(self):
        now = pygame.time.get_ticks()
        if self.active_powerup == "nitro" and now >= self.powerup_end:
            # remove nitro boost gently
            self._speed[0] = max(self._speed[0] - self._nitro_boost,
                                 self.diff["speed"])
            self.active_powerup = None
        elif self.active_powerup == "shield" and now >= self.powerup_end:
            self.active_powerup = None
            self.shield_active  = False
            self.player.shielded = False

    def _spawn_event(self):
        s = SpeedBump(self._speed)
        self.bumps.add(s)

    def _crash(self):
        if self.shield_active:
            # shield absorbs one hit
            self.shield_active = False
            self.active_powerup = None
            self.player.shielded = False
            # remove that enemy to avoid instant re-collision
            hits = pygame.sprite.spritecollide(self.player, self.enemies, False)
            for h in hits:
                h._reset()
            return
        # real crash
        self._play(self.crash_sound)
        pygame.mixer.music.stop()
        self._stop_timers()
        self.alive = False
        self.result = {
            "score":    self._score[0] * 10 + self.coin_points + self.distance // 10,
            "distance": self.distance,
            "coins":    self.coin_points,
        }

    # ── public update / draw ──────────────────────────────────────────────────

    def update(self, events):
        if not self.alive:
            return self.result

        for e in events:
            if e.type == self.INC_SPEED:
                # difficulty-based speed ramp, capped at 10
                self._speed[0] = min(self._speed[0] + self.diff["inc"], 10)
                # add one extra enemy every 50 score points, cap at 3
                target_enemies = self.diff["enemies"] + (self._score[0] // 50)
                target_enemies = min(target_enemies, 3)
                while len(self.enemies) < target_enemies:
                    en = Enemy(self._speed, self._score)
                    self.enemies.add(en)
                    self.all_sprites.add(en)

            elif e.type == self.SPAWN_COIN:
                c = Coin(self.enemies, self._speed)
                self.coins.add(c)
                self.all_sprites.add(c)

            elif e.type == self.SPAWN_OBS:
                oil = OilSpill(self._speed, on_exit=self._oil_scroll_away)
                self.oils.add(oil)

            elif e.type == self.SPAWN_PU:
                if len(self.powerups) < 2:
                    pu = PowerUp(self._speed)
                    self.powerups.add(pu)
                    self.all_sprites.add(pu)

            elif e.type == self.SPAWN_EVENT:
                self._spawn_event()

            elif e.type == self.SPAWN_OBSTACLE:
                obs = RoadObstacle(self._speed)
                self.obstacles.add(obs)

        # move everything
        for s in self.all_sprites:
            s.move()
        for s in self.oils:
            s.move()
        for s in self.bumps:
            s.move()
        for s in self.obstacles:
            s.move()

        # distance meter
        self.distance_timer += self._speed[0]
        if self.distance_timer >= 10:
            self.distance      += 1
            self.distance_timer = 0

        # speed flash countdown
        if self.speed_flash > 0:
            self.speed_flash -= 1

        # expire power-up
        self._expire_powerup()

        # ── coin collection ──────────────────────────────────────────────────
        collected = pygame.sprite.spritecollide(self.player, self.coins, True)
        if collected:
            self._play(self.coin_sound)
            for c in collected:
                self.coin_points += c.points
            milestone = self.coin_points // self.coin_milestone
            if milestone > self.last_milestone:
                self._speed[0]   = min(self._speed[0] + 0.5, 10)
                self.last_milestone = milestone
                self.speed_flash    = 90

        # ── power-up collection ───────────────────────────────────────────────
        pu_hits = pygame.sprite.spritecollide(self.player, self.powerups, True)
        for pu in pu_hits:
            self._apply_powerup(pu.kind)

        # ── oil spill effect  ────────────────────────────────────────────────
        oil_hits = pygame.sprite.spritecollide(self.player, self.oils, False)
        if oil_hits and not self._oil_applied:
            self._oil_applied = True
            self.on_oil       = True
            self._speed[0]    = max(self._speed[0] - self._OIL_SLOW, 1.0)
        elif not oil_hits and self._oil_applied:
            self._oil_applied = False
            self.on_oil       = False
            self._speed[0]    = min(self._speed[0] + self._OIL_SLOW, 10)


        pygame.sprite.spritecollide(self.player, self.bumps, True)


        if pygame.sprite.spritecollideany(self.player, self.obstacles):
            self._crash()


        enemy_hit = pygame.sprite.spritecollideany(self.player, self.enemies)
        if enemy_hit:
            self._crash()

        return None   # game continues

    def draw(self):
        self.bg.update_and_draw(self.surf)

        # shield aura around player
        if self.shield_active:
            cx, cy = self.player.rect.center
            pygame.draw.circle(self.surf, PURPLE, (cx, cy), 38, 3)

        # draw all sprites
        for s in self.all_sprites:
            self.surf.blit(s.image, s.rect)

        # draw hazards, nitro strips and power-ups (kept in separate groups)
        for s in self.oils:
            self.surf.blit(s.image, s.rect)
        for s in self.bumps:
            self.surf.blit(s.image, s.rect)
        for s in self.powerups:
            self.surf.blit(s.image, s.rect)
        for s in self.obstacles:
            self.surf.blit(s.image, s.rect)

        # HUD: score top-left
        sc = self.f_small.render(f"Score: {self._score[0]}", True, BLACK)
        self.surf.blit(sc, (10, 10))

        # HUD: coins top-right
        ct = self.f_small.render(f"Coins: {self.coin_points}", True, GOLD)
        cr = ct.get_rect(topright=(self.W - 10, 10))
        self.surf.blit(ct, cr)

        # HUD: distance
        dt = self.f_small.render(f"Dist: {self.distance}m", True, BLACK)
        dr = dt.get_rect(center=(self.W // 2, 14))
        self.surf.blit(dt, dr)

        # HUD: active power-up
        if self.active_powerup:
            now = pygame.time.get_ticks()
            if self.active_powerup == "nitro":
                remaining = max(0, (self.powerup_end - now) // 1000)
                label = f"NITRO {remaining}s"
                col   = CYAN
            elif self.active_powerup == "shield":
                label = "SHIELD ACTIVE"
                col   = PURPLE
            else:
                label = ""
                col   = WHITE
            if label:
                ps = self.f_pu.render(label, True, col)
                pr = ps.get_rect(center=(self.W // 2, 38))
                bg = pygame.Surface((pr.width + 16, pr.height + 8), pygame.SRCALPHA)
                bg.fill((0, 0, 0, 140))
                self.surf.blit(bg, (pr.x - 8, pr.y - 4))
                self.surf.blit(ps, pr)

        # oil warning
        if self.on_oil:
            ow = self.f_pu.render("OIL! Slow!", True, (200, 200, 0))
            self.surf.blit(ow, ow.get_rect(center=(self.W // 2, 60)))

        # speed up flash
        if self.speed_flash > 0:
            fs = self.f_flash.render("Speed Up!", True, RED)
            fr = fs.get_rect(center=(self.W // 2, self.H // 2 - 80))
            self.surf.blit(fs, fr)