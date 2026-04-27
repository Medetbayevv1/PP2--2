"""
ui.py – all non-gameplay screens for the Racer game.
Each class exposes:
  • update(events) → action string or None
  • draw()
"""

import pygame
from pygame.locals import *

# ── palette ───────────────────────────────────────────────────────────────────
BLACK  = (0,   0,   0)
WHITE  = (255, 255, 255)
GRAY   = (180, 180, 180)
DGRAY  = (60,  60,  60)
RED    = (220, 50,  50)
GREEN  = (50,  200, 80)
GOLD   = (255, 215, 0)
BLUE   = (30,  120, 220)
DARK   = (20,  20,  30)
PANEL  = (35,  35,  50)
ACCENT = (255, 200, 0)

# ── shared helpers ────────────────────────────────────────────────────────────

def _btn(surf, rect, text, font, bg=PANEL, fg=WHITE, hover=False):
    """Draw a rounded button; return True if mouse is hovering."""
    mx, my = pygame.mouse.get_pos()
    is_hov = rect.collidepoint(mx, my) if hover else False
    color  = (min(bg[0]+40, 255), min(bg[1]+40, 255), min(bg[2]+40, 255)) if is_hov else bg
    pygame.draw.rect(surf, color, rect, border_radius=10)
    pygame.draw.rect(surf, ACCENT, rect, 2, border_radius=10)
    lbl = font.render(text, True, fg)
    surf.blit(lbl, lbl.get_rect(center=rect.center))
    return is_hov


def _clicked(events, rect):
    for e in events:
        if e.type == MOUSEBUTTONDOWN and e.button == 1:
            if rect.collidepoint(e.pos):
                return True
    return False


def _draw_bg(surf):
    surf.fill(DARK)
    # subtle vertical gradient stripes
    for i in range(0, surf.get_width(), 40):
        pygame.draw.line(surf, (30, 30, 45), (i, 0), (i, surf.get_height()))


# ── MainMenu ──────────────────────────────────────────────────────────────────

class MainMenu:
    def __init__(self, surf, settings):
        self.surf     = surf
        self.settings = settings
        self.W, self.H = surf.get_size()
        self.font_title = pygame.font.SysFont("Verdana", 44, bold=True)
        self.font_btn   = pygame.font.SysFont("Verdana", 22, bold=True)
        self.font_sub   = pygame.font.SysFont("Verdana", 14)

        bw, bh, gap = 220, 50, 16
        cx = self.W // 2
        labels = ["Play", "Leaderboard", "Settings", "Quit"]
        self.buttons = {}
        for i, lbl in enumerate(labels):
            y = 260 + i * (bh + gap)
            self.buttons[lbl.lower()] = pygame.Rect(cx - bw//2, y, bw, bh)

    def update(self, events):
        for key, rect in self.buttons.items():
            if _clicked(events, rect):
                return key
        return None

    def draw(self):
        _draw_bg(self.surf)
        # title
        title = self.font_title.render("🏎  RACER", True, ACCENT)
        self.surf.blit(title, title.get_rect(center=(self.W//2, 120)))
        sub = self.font_sub.render("Dodge traffic · Collect coins · Set records", True, GRAY)
        self.surf.blit(sub, sub.get_rect(center=(self.W//2, 175)))
        # road stripe decoration
        for y in range(200, 220, 6):
            pygame.draw.line(self.surf, DGRAY, (0, y), (self.W, y))
        # buttons
        for key, rect in self.buttons.items():
            label = key.capitalize()
            _btn(self.surf, rect, label, self.font_btn, hover=True)


# ── UsernameScreen ─────────────────────────────────────────────────────────────

class UsernameScreen:
    def __init__(self, surf, settings):
        self.surf     = surf
        self.settings = settings
        self.W, self.H = surf.get_size()
        self.font_t   = pygame.font.SysFont("Verdana", 30, bold=True)
        self.font_inp = pygame.font.SysFont("Verdana", 26, bold=True)
        self.font_btn = pygame.font.SysFont("Verdana", 22, bold=True)
        self.font_sub = pygame.font.SysFont("Verdana", 15)
        self.name     = ""
        self.input_rect = pygame.Rect(self.W//2 - 140, 280, 280, 50)
        self.start_rect = pygame.Rect(self.W//2 - 100, 370, 200, 50)
        self.active   = True

    def update(self, events):
        for e in events:
            if e.type == KEYDOWN and self.active:
                if e.key == K_RETURN:
                    return "start:" + self.name.strip()
                elif e.key == K_BACKSPACE:
                    self.name = self.name[:-1]
                elif len(self.name) < 14:
                    if e.unicode.isprintable():
                        self.name += e.unicode
        if _clicked(events, self.start_rect):
            return "start:" + self.name.strip()
        return None

    def draw(self):
        _draw_bg(self.surf)
        title = self.font_t.render("Enter your name", True, ACCENT)
        self.surf.blit(title, title.get_rect(center=(self.W//2, 180)))
        hint = self.font_sub.render("Press Enter or click Start", True, GRAY)
        self.surf.blit(hint, hint.get_rect(center=(self.W//2, 230)))
        # input box
        pygame.draw.rect(self.surf, WHITE, self.input_rect, border_radius=8)
        pygame.draw.rect(self.surf, ACCENT, self.input_rect, 2, border_radius=8)
        name_surf = self.font_inp.render(self.name + "|", True, DARK)
        self.surf.blit(name_surf, name_surf.get_rect(center=self.input_rect.center))
        # start button
        _btn(self.surf, self.start_rect, "Start", self.font_btn, bg=GREEN, hover=True)


# ── GameOverScreen ────────────────────────────────────────────────────────────

class GameOverScreen:
    def __init__(self, surf, result, settings):
        self.surf     = surf
        self.result   = result      # {score, distance, coins}
        self.settings = settings
        self.W, self.H = surf.get_size()
        self.font_big  = pygame.font.SysFont("Verdana", 46, bold=True)
        self.font_med  = pygame.font.SysFont("Verdana", 22, bold=True)
        self.font_sm   = pygame.font.SysFont("Verdana", 17)
        bw, bh = 180, 48
        cx = self.W // 2
        self.retry_rect = pygame.Rect(cx - bw - 10, 450, bw, bh)
        self.menu_rect  = pygame.Rect(cx + 10,      450, bw, bh)

    def update(self, events):
        if _clicked(events, self.retry_rect): return "retry"
        if _clicked(events, self.menu_rect):  return "menu"
        return None

    def draw(self):
        self.surf.fill((180, 20, 20))
        title = self.font_big.render("GAME OVER", True, WHITE)
        self.surf.blit(title, title.get_rect(center=(self.W//2, 130)))
        # stats
        r = self.result
        stats = [
            f"Score     :  {r.get('score', 0)}",
            f"Distance  :  {r.get('distance', 0)} m",
            f"Coins     :  {r.get('coins', 0)} pts",
        ]
        for i, line in enumerate(stats):
            s = self.font_med.render(line, True, WHITE)
            self.surf.blit(s, s.get_rect(center=(self.W//2, 240 + i * 50)))
        # buttons
        _btn(self.surf, self.retry_rect, "Retry",     self.font_med, bg=GREEN, hover=True)
        _btn(self.surf, self.menu_rect,  "Main Menu", self.font_med, bg=PANEL, hover=True)


# ── LeaderboardScreen ──────────────────────────────────────────────────────────

class LeaderboardScreen:
    def __init__(self, surf, leaderboard, settings):
        self.surf        = surf
        self.leaderboard = leaderboard
        self.settings    = settings
        self.W, self.H   = surf.get_size()
        self.font_t  = pygame.font.SysFont("Verdana", 30, bold=True)
        self.font_h  = pygame.font.SysFont("Verdana", 15, bold=True)
        self.font_r  = pygame.font.SysFont("Verdana", 14)
        self.back_rect = pygame.Rect(self.W//2 - 80, 545, 160, 42)

    def update(self, events):
        if _clicked(events, self.back_rect): return "back"
        return None

    def draw(self):
        _draw_bg(self.surf)
        title = self.font_t.render("🏆  TOP 10", True, GOLD)
        self.surf.blit(title, title.get_rect(center=(self.W//2, 40)))
        # column headers
        headers = ["#", "Name", "Score", "Dist", "Coins"]
        xs      = [20, 55, 185, 270, 340]
        for hdr, x in zip(headers, xs):
            s = self.font_h.render(hdr, True, ACCENT)
            self.surf.blit(s, (x, 80))
        pygame.draw.line(self.surf, ACCENT, (15, 100), (self.W - 15, 100), 1)
        # rows
        medal = ["🥇","🥈","🥉"]
        for i, entry in enumerate(self.leaderboard[:10]):
            y   = 110 + i * 42
            bg  = (40, 40, 60) if i % 2 == 0 else (30, 30, 45)
            pygame.draw.rect(self.surf, bg, (15, y, self.W - 30, 38), border_radius=5)
            rank_str = medal[i] if i < 3 else str(i + 1)
            row = [
                rank_str,
                entry.get("name","?")[:10],
                str(entry.get("score", 0)),
                str(entry.get("distance", 0)) + "m",
                str(entry.get("coins", 0)),
            ]
            colors = [GOLD if i < 3 else WHITE] + [WHITE] * 4
            for val, x, col in zip(row, xs, colors):
                s = self.font_r.render(val, True, col)
                self.surf.blit(s, (x, y + 10))
        _btn(self.surf, self.back_rect, "Back", self.font_h, hover=True)


# ── SettingsScreen ─────────────────────────────────────────────────────────────

class SettingsScreen:
    def __init__(self, surf, settings):
        self.surf     = surf
        self.settings = settings          # mutated in-place
        self.W, self.H = surf.get_size()
        self.font_t  = pygame.font.SysFont("Verdana", 30, bold=True)
        self.font_lbl= pygame.font.SysFont("Verdana", 18, bold=True)
        self.font_val= pygame.font.SysFont("Verdana", 18)
        self.font_btn= pygame.font.SysFont("Verdana", 18, bold=True)

        # control rectangles  (toggle areas)
        self.sound_rect = pygame.Rect(240, 155, 100, 36)
        self.color_rects = {
            "blue": pygame.Rect(160, 240, 80, 36),
            "red":  pygame.Rect(260, 240, 80, 36),
        }
        self.diff_rects = {
            "easy":   pygame.Rect(50,  330, 90, 36),
            "normal": pygame.Rect(155, 330, 90, 36),
            "hard":   pygame.Rect(260, 330, 90, 36),
        }
        self.back_rect = pygame.Rect(self.W//2 - 80, 500, 160, 44)

    def update(self, events):
        if _clicked(events, self.sound_rect):
            self.settings["sound"] = not self.settings["sound"]
        for col, r in self.color_rects.items():
            if _clicked(events, r):
                self.settings["car_color"] = col
        for diff, r in self.diff_rects.items():
            if _clicked(events, r):
                self.settings["difficulty"] = diff
        if _clicked(events, self.back_rect):
            return "back"
        return None

    def draw(self):
        _draw_bg(self.surf)
        title = self.font_t.render("⚙  Settings", True, ACCENT)
        self.surf.blit(title, title.get_rect(center=(self.W//2, 60)))

        # Sound toggle
        self._section_label("Sound", 160)
        on_off = "ON" if self.settings["sound"] else "OFF"
        col    = GREEN if self.settings["sound"] else RED
        _btn(self.surf, self.sound_rect, on_off, self.font_btn, bg=col, hover=True)

        # Car color
        self._section_label("Car Color", 250)
        for col_key, r in self.color_rects.items():
            active = self.settings["car_color"] == col_key
            bg = (30,100,200) if col_key == "blue" else (200,40,40)
            border = ACCENT if active else GRAY
            pygame.draw.rect(self.surf, bg, r, border_radius=8)
            pygame.draw.rect(self.surf, border, r, 3, border_radius=8)
            lbl = self.font_val.render(col_key.capitalize(), True, WHITE)
            self.surf.blit(lbl, lbl.get_rect(center=r.center))

        # Difficulty
        self._section_label("Difficulty", 340)
        diff_colors = {"easy": (40,160,80), "normal": (200,150,0), "hard": (200,40,40)}
        for diff_key, r in self.diff_rects.items():
            active = self.settings["difficulty"] == diff_key
            bg = diff_colors[diff_key]
            border = ACCENT if active else GRAY
            pygame.draw.rect(self.surf, bg, r, border_radius=8)
            pygame.draw.rect(self.surf, border, r, 3, border_radius=8)
            lbl = self.font_val.render(diff_key.capitalize(), True, WHITE)
            self.surf.blit(lbl, lbl.get_rect(center=r.center))

        _btn(self.surf, self.back_rect, "Save & Back", self.font_btn, hover=True)

    def _section_label(self, text, y):
        lbl = self.font_lbl.render(text + ":", True, GRAY)
        self.surf.blit(lbl, (30, y))