# db.py — PostgreSQL persistence layer (psycopg2)

import psycopg2
import psycopg2.extras

# ── Connection ────────────────────────────────────────────────────

def get_connection():
    """Return a new psycopg2 connection.  Edit DSN to match your setup."""
    return psycopg2.connect(
        host="localhost",
        port=5432,
        dbname="snake_game",
        user="postgres",
        password="postgres",
    )


# ── Schema bootstrap ──────────────────────────────────────────────

def init_db():
    """Create tables if they don't exist yet."""
    ddl = """
    CREATE TABLE IF NOT EXISTS players (
        id       SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_sessions (
        id            SERIAL PRIMARY KEY,
        player_id     INTEGER REFERENCES players(id),
        score         INTEGER   NOT NULL,
        level_reached INTEGER   NOT NULL,
        played_at     TIMESTAMP DEFAULT NOW()
    );
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(ddl)
    except Exception as e:
        print(f"[DB] init_db error: {e}")


# ── Player helpers ────────────────────────────────────────────────

def get_or_create_player(username: str) -> int:
    """Return player id, creating the row if needed."""
    sql_select = "SELECT id FROM players WHERE username = %s"
    sql_insert = "INSERT INTO players (username) VALUES (%s) RETURNING id"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql_select, (username,))
                row = cur.fetchone()
                if row:
                    return row[0]
                cur.execute(sql_insert, (username,))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        return -1


def save_session(player_id: int, score: int, level_reached: int):
    """Insert a completed game session."""
    sql = """
        INSERT INTO game_sessions (player_id, score, level_reached)
        VALUES (%s, %s, %s)
    """
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (player_id, score, level_reached))
    except Exception as e:
        print(f"[DB] save_session error: {e}")


def get_personal_best(player_id: int) -> int:
    """Return the player's highest score ever, or 0."""
    sql = "SELECT COALESCE(MAX(score), 0) FROM game_sessions WHERE player_id = %s"
    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (player_id,))
                return cur.fetchone()[0]
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0


def get_leaderboard(limit: int = 10) -> list[dict]:
    """Return top *limit* rows from game_sessions joined with players."""
    sql = """
        SELECT p.username,
               gs.score,
               gs.level_reached,
               gs.played_at::date AS played_date
        FROM game_sessions gs
        JOIN players p ON p.id = gs.player_id
        ORDER BY gs.score DESC, gs.played_at DESC
        LIMIT %s
    """
    try:
        with get_connection() as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
                cur.execute(sql, (limit,))
                return [dict(r) for r in cur.fetchall()]
    except Exception as e:
        print(f"[DB] get_leaderboard error: {e}")
        return []
