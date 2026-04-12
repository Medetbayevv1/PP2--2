"""
Simple Music Player with Keyboard Controls
==========================================
Controls:
  P  - Play current track
  S  - Stop playback
  N  - Next track
  B  - Previous (Back) track
  Q  - Quit
"""

import pygame
import sys
from player import MusicPlayer

# ── Window settings ──────────────────────────────────────────────────────────
WIDTH, HEIGHT = 480, 300
FPS = 30

# ── Colors ────────────────────────────────────────────────────────────────────
BG_COLOR       = (20,  20,  35)   # dark navy background
PANEL_COLOR    = (35,  35,  55)   # slightly lighter panel
ACCENT_COLOR   = (100, 180, 255)  # sky-blue accent
TEXT_COLOR     = (230, 230, 255)  # near-white text
DIM_COLOR      = (110, 110, 150)  # muted text
PLAYING_COLOR  = (80,  220, 120)  # green when playing
STOPPED_COLOR  = (220,  80,  80)  # red when stopped
BAR_BG_COLOR   = (50,   50,  80)  # progress bar background
BAR_FG_COLOR   = (100, 180, 255)  # progress bar fill


def draw_ui(screen, fonts, player):
    """Redraw the entire player UI each frame."""
    screen.fill(BG_COLOR)

    # ── Title bar ─────────────────────────────────────────────────────────────
    title_surf = fonts["big"].render("Music Player", True, ACCENT_COLOR)
    screen.blit(title_surf, (WIDTH // 2 - title_surf.get_width() // 2, 20))

    # ── Panel ─────────────────────────────────────────────────────────────────
    panel_rect = pygame.Rect(30, 65, WIDTH - 60, 150)
    pygame.draw.rect(screen, PANEL_COLOR, panel_rect, border_radius=12)

    # ── Track name ────────────────────────────────────────────────────────────
    track_name = player.get_track_name()
    track_surf = fonts["medium"].render(track_name, True, TEXT_COLOR)
    screen.blit(track_surf, (WIDTH // 2 - track_surf.get_width() // 2, 85))

    # ── Track counter (e.g. "2 / 3") ─────────────────────────────────────────
    if player.playlist:
        counter_text = f"{player.current_index + 1} / {len(player.playlist)}"
    else:
        counter_text = "0 / 0"
    counter_surf = fonts["small"].render(counter_text, True, DIM_COLOR)
    screen.blit(counter_surf, (WIDTH // 2 - counter_surf.get_width() // 2, 115))

    # ── Status badge ──────────────────────────────────────────────────────────
    if player.is_playing:
        status_text  = "PLAYING"
        status_color = PLAYING_COLOR
    else:
        status_text  = "STOPPED"
        status_color = STOPPED_COLOR
    status_surf = fonts["medium"].render(status_text, True, status_color)
    screen.blit(status_surf, (WIDTH // 2 - status_surf.get_width() // 2, 145))

    # ── Progress bar ──────────────────────────────────────────────────────────
    bar_x, bar_y = 60, 183
    bar_w, bar_h = WIDTH - 120, 12
    pygame.draw.rect(screen, BAR_BG_COLOR, (bar_x, bar_y, bar_w, bar_h), border_radius=6)

    elapsed = player.get_elapsed_seconds()
    # We don't know the real duration of a WAV easily, so we show 30-second loops
    DISPLAY_DURATION = 30
    progress = min(elapsed / DISPLAY_DURATION, 1.0)
    fill_w = int(bar_w * progress)
    if fill_w > 0:
        pygame.draw.rect(screen, BAR_FG_COLOR, (bar_x, bar_y, fill_w, bar_h), border_radius=6)

    # ── Keyboard hints ────────────────────────────────────────────────────────
    hints = "[P] Play   [S] Stop   [N] Next   [B] Back   [Q] Quit"
    hint_surf = fonts["small"].render(hints, True, DIM_COLOR)
    screen.blit(hint_surf, (WIDTH // 2 - hint_surf.get_width() // 2, 250))

    pygame.display.flip()


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Simple Music Player")
    clock = pygame.time.Clock()

    # ── Fonts ─────────────────────────────────────────────────────────────────
    fonts = {
        "big":    pygame.font.SysFont("segoeui", 26, bold=True),
        "medium": pygame.font.SysFont("segoeui", 20),
        "small":  pygame.font.SysFont("segoeui", 14),
    }

    # ── Player ────────────────────────────────────────────────────────────────
    player = MusicPlayer(music_folder="music")

    # ── Main loop ─────────────────────────────────────────────────────────────
    running = True
    while running:
        for event in pygame.event.get():

            # Close button clicked
            if event.type == pygame.QUIT:
                running = False

            # Keyboard input
            elif event.type == pygame.KEYDOWN:
                key = event.key

                if key == pygame.K_p:          # P → Play
                    player.play()
                    print(f"Playing: {player.get_track_name()}")

                elif key == pygame.K_s:        # S → Stop
                    player.stop()
                    print("Stopped.")

                elif key == pygame.K_n:        # N → Next
                    player.next_track()
                    print(f"Next track: {player.get_track_name()}")

                elif key == pygame.K_b:        # B → Back / Previous
                    player.previous_track()
                    print(f"Previous track: {player.get_track_name()}")

                elif key == pygame.K_q:        # Q → Quit
                    running = False

        # Auto-advance when a track finishes naturally
        if player.is_playing and not pygame.mixer.music.get_busy():
            player.next_track()

        draw_ui(screen, fonts, player)
        clock.tick(FPS)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()