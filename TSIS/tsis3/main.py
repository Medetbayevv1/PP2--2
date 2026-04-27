import pygame, sys
from pygame.locals import *
from ui import MainMenu, LeaderboardScreen, SettingsScreen, UsernameScreen, GameOverScreen
from racer import GameSession
from persistence import load_settings, save_settings, load_leaderboard, save_leaderboard

pygame.init()
pygame.mixer.init()

SCREEN_WIDTH = 400
SCREEN_HEIGHT = 600
DISPLAYSURF = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Racer")

FPS = 60
clock = pygame.time.Clock()

# ── state machine ──────────────────────────────────────────────
STATE_MENU        = "menu"
STATE_USERNAME    = "username"
STATE_GAME        = "game"
STATE_GAMEOVER    = "gameover"
STATE_LEADERBOARD = "leaderboard"
STATE_SETTINGS    = "settings"

def main():
    settings    = load_settings()
    leaderboard = load_leaderboard()
    username    = "Player"
    last_result = None          # dict returned by GameSession

    state = STATE_MENU
    screen_obj = MainMenu(DISPLAYSURF, settings)

    while True:
        events = pygame.event.get()
        for e in events:
            if e.type == QUIT:
                pygame.quit(); sys.exit()

        # ── MENU ──────────────────────────────────────────────
        if state == STATE_MENU:
            action = screen_obj.update(events)
            screen_obj.draw()
            if action == "play":
                state      = STATE_USERNAME
                screen_obj = UsernameScreen(DISPLAYSURF, settings)
            elif action == "leaderboard":
                state      = STATE_LEADERBOARD
                screen_obj = LeaderboardScreen(DISPLAYSURF, leaderboard, settings)
            elif action == "settings":
                state      = STATE_SETTINGS
                screen_obj = SettingsScreen(DISPLAYSURF, settings)
            elif action == "quit":
                pygame.quit(); sys.exit()

        # ── USERNAME ──────────────────────────────────────────
        elif state == STATE_USERNAME:
            action = screen_obj.update(events)
            screen_obj.draw()
            if action and action.startswith("start:"):
                username   = action[6:] or "Player"
                state      = STATE_GAME
                session    = GameSession(DISPLAYSURF, settings)

        # ── GAME ──────────────────────────────────────────────
        elif state == STATE_GAME:
            result = session.update(events)
            session.draw()
            if result is not None:
                last_result = result
                # save to leaderboard
                leaderboard.append({
                    "name":     username,
                    "score":    result["score"],
                    "distance": result["distance"],
                    "coins":    result["coins"],
                })
                leaderboard.sort(key=lambda x: x["score"], reverse=True)
                leaderboard = leaderboard[:10]
                save_leaderboard(leaderboard)
                state      = STATE_GAMEOVER
                screen_obj = GameOverScreen(DISPLAYSURF, last_result, settings)

        # ── GAME OVER ─────────────────────────────────────────
        elif state == STATE_GAMEOVER:
            action = screen_obj.update(events)
            screen_obj.draw()
            if action == "retry":
                state   = STATE_GAME
                session = GameSession(DISPLAYSURF, settings)
            elif action == "menu":
                state      = STATE_MENU
                screen_obj = MainMenu(DISPLAYSURF, settings)

        # ── LEADERBOARD ───────────────────────────────────────
        elif state == STATE_LEADERBOARD:
            action = screen_obj.update(events)
            screen_obj.draw()
            if action == "back":
                state      = STATE_MENU
                screen_obj = MainMenu(DISPLAYSURF, settings)

        # ── SETTINGS ──────────────────────────────────────────
        elif state == STATE_SETTINGS:
            action = screen_obj.update(events)
            screen_obj.draw()
            if action == "back":
                save_settings(settings)
                state      = STATE_MENU
                screen_obj = MainMenu(DISPLAYSURF, settings)

        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()