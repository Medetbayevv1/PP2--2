# Snake Game — TSIS 4

Extended Snake game with PostgreSQL leaderboard, power-ups, obstacles, poison food, settings, and multiple game screens.

## Requirements

```
pip install pygame psycopg2-binary
```

## PostgreSQL Setup

1. Create a database:
```sql
CREATE DATABASE snake_game;
```

2. Update the connection settings in `db.py` (`get_connection()`) if your PostgreSQL credentials differ from the defaults:
   - host: `localhost`
   - port: `5432`
   - dbname: `snake_game`
   - user: `postgres`
   - password: `postgres`

3. The tables (`players`, `game_sessions`) are created automatically on first run.

## Run

```bash
python main.py
```

## Project Structure

```
TSIS4/
├── main.py          # Game screens: Main Menu, Game Over, Leaderboard, Settings
├── game.py          # Core game loop and rendering
├── db.py            # PostgreSQL persistence (psycopg2)
├── config.py        # All tunable constants
├── settings.json    # User preferences (auto-created/updated)
└── assets/
    └── coin.mp3     # Pickup sound effect
```

## Features

| Feature | Details |
|---|---|
| **Main Menu** | Username entry, Play / Leaderboard / Settings / Quit |
| **Leaderboard** | Top 10 all-time scores from PostgreSQL |
| **Personal Best** | Shown during gameplay and on Game Over screen |
| **Food types** | Common, Bonus, Rare, Epic (timed + weighted), Poison |
| **Poison food** | Shortens snake by 2; game over if too short |
| **Power-ups** | Speed Boost, Slow Motion, Shield (8 s field life, 5 s effect) |
| **Obstacles** | Random wall blocks from Level 3 onward |
| **Settings** | Snake color, grid overlay, sound — saved to `settings.json` |
| **Game Over** | Score, level, personal best, Retry / Main Menu |

## Controls

| Key | Action |
|---|---|
| Arrow keys | Move snake |
| R (Game Over) | Retry |
| ESC (Game Over / Settings) | Back to menu / discard |
