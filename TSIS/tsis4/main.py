# main.py — Screens: Main Menu, Game Over, Leaderboard, Settings

import json
import os
import pygame

import db
from config import WINDOW_X, WINDOW_Y
from game import GameSession

# ── Settings file ─────────────────────────────────────────────────

SETTINGS_FILE = os.path.join(os.path.dirname(__file__), "settings.json")

DEFAULT_SETTINGS = {
    "snake_color": [0, 255, 0],
    "grid": False,
    "sound": True,
}


def load_settings() -> dict:
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, "r") as f:
                data = json.load(f)
                # Fill in any missing keys
                for k, v in DEFAULT_SETTINGS.items():
                    data.setdefault(k, v)
                return data
        except Exception:
            pass
    return dict(DEFAULT_SETTINGS)


def save_settings(settings: dict):
    try:
        with open(SETTINGS_FILE, "w") as f:
            json.dump(settings, f, indent=2)
    except Exception as e:
        print(f"[Settings] save error: {e}")


# ── Pygame init ───────────────────────────────────────────────────

pygame.init()
pygame.mixer.init()
screen = pygame.display.set_mode((WINDOW_X, WINDOW_Y))
pygame.display.set_caption("Snake Game — TSIS 4")
clock  = pygame.time.Clock()

# Fonts
F_TITLE  = pygame.font.SysFont("consolas", 52, bold=True)
F_LARGE  = pygame.font.SysFont("consolas", 36, bold=True)
F_MED    = pygame.font.SysFont("consolas", 24)
F_SMALL  = pygame.font.SysFont("consolas", 18)

# Colours
BLACK    = (0,   0,   0)
WHITE    = (255, 255, 255)
GREEN    = (0,   255,  0)
RED      = (220,  30,  30)
YELLOW   = (255, 215,  0)
GRAY     = (80,  80,  80)
LGRAY    = (160, 160, 160)
DGRAY    = (25,  25,  25)
ACCENT   = (0,   200, 120)

# Load coin sound (optional — graceful fallback if missing)
_sound_path = os.path.join(os.path.dirname(__file__), "assets", "coin.mp3")
try:
    coin_sound = pygame.mixer.Sound(_sound_path)
except Exception:
    coin_sound = None
    print("[Audio] coin.mp3 not found — sound disabled")


# ── UI primitives ──────────────────────────────────────────────────

def draw_background():
    screen.fill((10, 10, 10))
    # Subtle grid lines
    for x in range(0, WINDOW_X, 30):
        pygame.draw.line(screen, (20, 20, 20), (x, 0), (x, WINDOW_Y))
    for y in range(0, WINDOW_Y, 30):
        pygame.draw.line(screen, (20, 20, 20), (0, y), (WINDOW_X, y))


def draw_button(rect: pygame.Rect, text: str,
                hover: bool = False, color=None) -> pygame.Rect:
    bg    = color or (ACCENT if hover else GRAY)
    tc    = BLACK if hover else WHITE
    pygame.draw.rect(screen, bg,  rect, border_radius=6)
    pygame.draw.rect(screen, LGRAY, rect, 1, border_radius=6)
    surf  = F_MED.render(text, True, tc)
    screen.blit(surf, surf.get_rect(center=rect.center))
    return rect


def text_center(surf, y, color=WHITE):
    r = surf.get_rect(midtop=(WINDOW_X // 2, y))
    screen.blit(surf, r)


def mouse_over(rect: pygame.Rect) -> bool:
    return rect.collidepoint(pygame.mouse.get_pos())


# ── Text input widget ──────────────────────────────────────────────

def get_text_input(prompt: str, max_len: int = 20) -> str:
    """Block until the user types a non-empty string and presses Enter."""
    text   = ""
    active = True
    while active:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and text.strip():
                    return text.strip()
                elif event.key == pygame.K_BACKSPACE:
                    text = text[:-1]
                elif len(text) < max_len and event.unicode.isprintable():
                    text += event.unicode

        draw_background()
        title = F_LARGE.render(prompt, True, ACCENT)
        text_center(title, 140)

        # Input box
        box = pygame.Rect(WINDOW_X // 2 - 160, 220, 320, 48)
        pygame.draw.rect(screen, DGRAY, box, border_radius=6)
        pygame.draw.rect(screen, ACCENT, box, 2, border_radius=6)
        inp_surf = F_MED.render(text + "|", True, WHITE)
        screen.blit(inp_surf, inp_surf.get_rect(midleft=(box.x + 12, box.centery)))

        hint = F_SMALL.render("Press ENTER to confirm", True, LGRAY)
        text_center(hint, 286)

        pygame.display.flip()
    return text


# ── Screens ────────────────────────────────────────────────────────

def screen_main_menu(settings: dict) -> str:
    """
    Returns: "play" | "leaderboard" | "settings" | "quit"
    Also updates settings["username"] and settings["player_id"].
    """
    buttons = {
        "play":        pygame.Rect(WINDOW_X // 2 - 110, 200, 220, 48),
        "leaderboard": pygame.Rect(WINDOW_X // 2 - 110, 264, 220, 48),
        "settings":    pygame.Rect(WINDOW_X // 2 - 110, 328, 220, 48),
        "quit":        pygame.Rect(WINDOW_X // 2 - 110, 392, 220, 48),
    }

    # Prompt username if not set
    if not settings.get("username"):
        settings["username"] = get_text_input("Enter your username:")
        pid = db.get_or_create_player(settings["username"])
        settings["player_id"]      = pid
        settings["personal_best"]  = db.get_personal_best(pid)

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            if event.type == pygame.MOUSEBUTTONDOWN:
                for action, rect in buttons.items():
                    if rect.collidepoint(event.pos):
                        return action
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    return "play"

        draw_background()

        title = F_TITLE.render("SNAKE GAME", True, GREEN)
        text_center(title, 100)

        sub = F_SMALL.render(f"Welcome, {settings['username']}  |  Best: {settings['personal_best']}", True, LGRAY)
        text_center(sub, 162)

        for action, rect in buttons.items():
            label = {"play": "Play", "leaderboard": "Leaderboard",
                     "settings": "Settings", "quit": "Quit"}[action]
            draw_button(rect, label, hover=mouse_over(rect))

        pygame.display.flip()


def screen_game_over(result: dict, settings: dict) -> str:
    """
    result: {"score": int, "level": int}
    Returns: "retry" | "menu"
    """
    score    = result["score"]
    level    = result["level"]
    pb       = settings.get("personal_best", 0)
    new_best = score > pb

    if new_best:
        settings["personal_best"] = score

    btn_retry = pygame.Rect(WINDOW_X // 2 - 120, 340, 220, 48)
    btn_menu  = pygame.Rect(WINDOW_X // 2 - 120, 404, 220, 48)

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "menu"
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_retry.collidepoint(event.pos): return "retry"
                if btn_menu.collidepoint(event.pos):  return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "retry"
                if event.key == pygame.K_ESCAPE: return "menu"

        draw_background()

        go_surf = F_LARGE.render("GAME OVER", True, RED)
        text_center(go_surf, 100)

        sc_surf = F_MED.render(f"Score: {score}   Level: {level}", True, WHITE)
        text_center(sc_surf, 170)

        pb_surf = F_MED.render(
            f"Personal Best: {settings['personal_best']}" +
            (" NEW BEST!" if new_best else ""),
            True, YELLOW if new_best else LGRAY
        )
        text_center(pb_surf, 214)

        hint = F_SMALL.render("R = Retry   ESC = Menu", True, GRAY)
        text_center(hint, 290)

        draw_button(btn_retry, "Retry",    hover=mouse_over(btn_retry))
        draw_button(btn_menu,  "Main Menu", hover=mouse_over(btn_menu))

        pygame.display.flip()


def screen_leaderboard(settings: dict):
    """Show Top 10 from DB.  Returns when user clicks Back or presses ESC."""
    rows   = db.get_leaderboard(10)
    btn_back = pygame.Rect(WINDOW_X // 2 - 80, WINDOW_Y - 60, 160, 44)

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_back.collidepoint(event.pos): return
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_ESCAPE, pygame.K_BACKSPACE): return

        draw_background()

        title = F_LARGE.render("Leaderboard", True, YELLOW)
        text_center(title, 24)

        if not rows:
            msg = F_MED.render("No scores yet — play a game!", True, LGRAY)
            text_center(msg, 200)
        else:
            # Table header
            hdr = F_SMALL.render(
                f"{'#':<4}{'Player':<18}{'Score':>7}{'Level':>7}{'Date':>12}",
                True, ACCENT
            )
            text_center(hdr, 80)
            pygame.draw.line(screen, GRAY,
                             (60, 100), (WINDOW_X - 60, 100), 1)

            for i, row in enumerate(rows):
                color  = YELLOW if i == 0 else (LGRAY if i < 3 else WHITE)
                line   = (
                    f"{i+1:<4}"
                    f"{str(row['username']):<18}"
                    f"{row['score']:>7}"
                    f"{row['level_reached']:>7}"
                    f"{str(row['played_date']):>12}"
                )
                surf   = F_SMALL.render(line, True, color)
                text_center(surf, 108 + i * 24)

        draw_button(btn_back, "← Back", hover=mouse_over(btn_back))
        pygame.display.flip()


def screen_settings(settings: dict):
    """Allows toggling grid, sound, and snake color.  Saves on exit."""
    # Preset colors
    COLORS = [
        ("Green",   [0,   255,   0]),
        ("Cyan",    [0,   255, 200]),
        ("Orange",  [255, 140,   0]),
        ("Pink",    [255,  80, 160]),
        ("White",   [255, 255, 255]),
    ]
    color_idx = 0
    for i, (_, rgb) in enumerate(COLORS):
        if rgb == settings.get("snake_color", DEFAULT_SETTINGS["snake_color"]):
            color_idx = i; break

    btn_grid   = pygame.Rect(WINDOW_X // 2 - 120, 160, 240, 44)
    btn_sound  = pygame.Rect(WINDOW_X // 2 - 120, 224, 240, 44)
    btn_color  = pygame.Rect(WINDOW_X // 2 - 120, 288, 240, 44)
    btn_save   = pygame.Rect(WINDOW_X // 2 - 120, 380, 240, 44)

    local = dict(settings)   # edit a copy; only apply on Save

    while True:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if event.type == pygame.MOUSEBUTTONDOWN:
                if btn_grid.collidepoint(event.pos):
                    local["grid"] = not local.get("grid", False)
                if btn_sound.collidepoint(event.pos):
                    local["sound"] = not local.get("sound", True)
                if btn_color.collidepoint(event.pos):
                    color_idx = (color_idx + 1) % len(COLORS)
                    local["snake_color"] = COLORS[color_idx][1]
                if btn_save.collidepoint(event.pos):
                    settings.update(local)
                    save_settings({k: v for k, v in settings.items()
                                   if k not in ("username", "player_id", "personal_best")})
                    return
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return   # discard

        draw_background()

        title = F_LARGE.render("Settings", True, ACCENT)
        text_center(title, 60)

        grid_on  = local.get("grid", False)
        sound_on = local.get("sound", True)
        c_name   = COLORS[color_idx][0]

        draw_button(btn_grid,  f"Grid Overlay:  {'ON' if grid_on else 'OFF'}",
                    hover=mouse_over(btn_grid),
                    color=ACCENT if grid_on else None)
        draw_button(btn_sound, f"Sound:  {'ON' if sound_on else 'OFF'}",
                    hover=mouse_over(btn_sound),
                    color=ACCENT if sound_on else None)

        # Color preview
        pygame.draw.rect(screen, pygame.Color(*local["snake_color"]),
                         pygame.Rect(btn_color.x - 30, btn_color.y + 10, 20, 20))
        draw_button(btn_color, f"Snake Color:  {c_name}", hover=mouse_over(btn_color))

        draw_button(btn_save,  "Save & Back", hover=mouse_over(btn_save), color=ACCENT)

        hint = F_SMALL.render("ESC = discard changes", True, GRAY)
        text_center(hint, WINDOW_Y - 30)

        pygame.display.flip()


# ── Entry point ────────────────────────────────────────────────────

def main():
    db.init_db()
    settings = load_settings()
    settings.setdefault("username", "")
    settings.setdefault("player_id", -1)
    settings.setdefault("personal_best", 0)

    while True:
        action = screen_main_menu(settings)

        if action == "quit":
            break
        elif action == "leaderboard":
            screen_leaderboard(settings)
        elif action == "settings":
            screen_settings(settings)
        elif action == "play":
            while True:
                session = GameSession(
                    screen    = screen,
                    settings  = settings,
                    coin_sound = coin_sound,
                    personal_best = settings.get("personal_best", 0),
                )
                result = session.run()

                # Persist result
                pid = settings.get("player_id", -1)
                if pid != -1:
                    db.save_session(pid, result["score"], result["level"])
                    # Refresh personal best
                    settings["personal_best"] = db.get_personal_best(pid)

                after = screen_game_over(result, settings)
                if after == "retry":
                    continue
                else:
                    break

    pygame.quit()


if __name__ == "__main__":
    main()
