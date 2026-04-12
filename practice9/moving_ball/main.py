"""
Moving Ball Game  —  Professional Edition
==========================================
Arrow keys to move (tap or hold)  |  Q / window close to quit
"""

import pygame
import sys
import math
from ball import Ball

# ── Window & timing ───────────────────────────────────────────────────────────
WIDTH, HEIGHT = 700, 500
FPS           = 60

# ── Palette  (dark arcade / neon) ─────────────────────────────────────────────
BG_DARK      = ( 10,  10,  18)
GRID_COLOR   = ( 25,  25,  45)
BALL_COLOR   = (255,  55,  85)
GLOW_COLOR   = (255,  80, 100)
TRAIL_COLOR  = (200,  30,  60)
HUD_ACCENT   = ( 80, 220, 180)
HUD_DIM      = ( 80,  90, 110)
WHITE        = (235, 235, 245)
BORDER_COLOR = ( 55,  60,  90)


# ── Drawing helpers ────────────────────────────────────────────────────────────

def draw_grid(surface):
    spacing = 40
    for gx in range(0, WIDTH, spacing):
        for gy in range(0, HEIGHT, spacing):
            pygame.draw.circle(surface, GRID_COLOR, (gx, gy), 1)


def draw_border(surface):
    pygame.draw.rect(surface, BORDER_COLOR, (0, 0, WIDTH, HEIGHT), 2)


def draw_trail(surface, ball):
    n = len(ball.trail)
    for i, (tx, ty) in enumerate(ball.trail):
        ratio  = (n - i) / ball.TRAIL_LEN
        alpha  = int(180 * ratio * ratio)
        radius = max(3, int(ball.RADIUS * ratio * 0.7))
        ghost  = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(ghost, (*TRAIL_COLOR, alpha), (radius, radius), radius)
        surface.blit(ghost, (tx - radius, ty - radius))


def draw_glow(surface, ball, tick):
    pulse  = 0.5 + 0.5 * math.sin(tick * 0.07)
    layers = [
        (ball.RADIUS + 22 + int(pulse * 6), 18),
        (ball.RADIUS + 12 + int(pulse * 4), 35),
        (ball.RADIUS +  5 + int(pulse * 2), 55),
    ]
    for radius, alpha in layers:
        glow = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(glow, (*GLOW_COLOR, alpha), (radius, radius), radius)
        surface.blit(glow, (ball.x - radius, ball.y - radius))


def draw_ball(surface, ball):
    pygame.draw.circle(surface, BALL_COLOR, (ball.x, ball.y), ball.RADIUS)
    pygame.draw.circle(surface, (255, 160, 175), (ball.x - 7, ball.y - 7), 7)


def draw_hud(surface, fonts, ball):
    lines = [
        (f"X  {ball.x:>4}   Y  {ball.y:>4}", HUD_ACCENT),
        (f"MOVES  {ball.moves:>5}",           WHITE),
    ]
    for i, (text, color) in enumerate(lines):
        surf = fonts["mono"].render(text, True, color)
        surface.blit(surf, (14, 12 + i * 22))


def draw_controls(surface, fonts):
    hint = "[Q] QUIT"
    surf = fonts["small"].render(hint, True, HUD_DIM)
    surface.blit(surf, (WIDTH // 2 - surf.get_width() // 2, HEIGHT - 24))


def draw_title(surface, fonts):
    surf = fonts["title"].render("BALL ARENA", True, BORDER_COLOR)
    surface.blit(surf, (WIDTH - surf.get_width() - 14, 12))


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Ball Arena")
    clock = pygame.time.Clock()

    fonts = {
        "title": pygame.font.SysFont("consolas", 18, bold=True),
        "mono":  pygame.font.SysFont("consolas", 16),
        "small": pygame.font.SysFont("consolas", 13),
    }

    ball = Ball(WIDTH, HEIGHT)
    tick = 0

    # Key-hold settings:
    #   INITIAL_DELAY_MS — pause before auto-repeat starts (feels like a real keyboard)
    #   REPEAT_MS        — interval between moves while key is held
    INITIAL_DELAY_MS = 180
    REPEAT_MS        = 60
    move_timer       = 0   # counts down to next held-key move

    running = True
    while running:
        dt    = clock.get_time()   # milliseconds since last frame
        tick += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.KEYDOWN:
                # Instant move on first press
                if   event.key == pygame.K_UP:    ball.move_up()
                elif event.key == pygame.K_DOWN:  ball.move_down()
                elif event.key == pygame.K_LEFT:  ball.move_left()
                elif event.key == pygame.K_RIGHT: ball.move_right()
                elif event.key == pygame.K_q:     running = False
                # Start the initial delay before repeat kicks in
                move_timer = INITIAL_DELAY_MS

            elif event.type == pygame.KEYUP:
                move_timer = 0   # reset when key is released

        # ── Held-key repeat ───────────────────────────────────────────────────
        keys = pygame.key.get_pressed()
        any_arrow = (keys[pygame.K_UP] or keys[pygame.K_DOWN] or
                     keys[pygame.K_LEFT] or keys[pygame.K_RIGHT])

        if any_arrow and move_timer > 0:
            move_timer -= dt
            if move_timer <= 0:
                if   keys[pygame.K_UP]:    ball.move_up()
                elif keys[pygame.K_DOWN]:  ball.move_down()
                elif keys[pygame.K_LEFT]:  ball.move_left()
                elif keys[pygame.K_RIGHT]: ball.move_right()
                move_timer = REPEAT_MS   # fast repeat from here on

        # ── Render ────────────────────────────────────────────────────────────
        screen.fill(BG_DARK)
        draw_grid(screen)
        draw_border(screen)
        draw_trail(screen, ball)
        draw_glow(screen, ball, tick)
        draw_ball(screen, ball)
        draw_hud(screen, fonts, ball)
        draw_title(screen, fonts)
        draw_controls(screen, fonts)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()