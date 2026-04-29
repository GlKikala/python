import psycopg2
from config import DB_CONFIG


def get_connection():
    """Connect Python to PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def create_tables():
    """Create players and game_sessions tables."""
    sql = """
    CREATE TABLE IF NOT EXISTS players (
        id SERIAL PRIMARY KEY,
        username VARCHAR(50) UNIQUE NOT NULL
    );

    CREATE TABLE IF NOT EXISTS game_sessions (
        id SERIAL PRIMARY KEY,
        player_id INTEGER REFERENCES players(id),
        score INTEGER NOT NULL,
        level_reached INTEGER NOT NULL,
        played_at TIMESTAMP DEFAULT NOW()
    );
    """

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(sql)
        conn.commit()


def get_or_create_player(username):
    """Return player id. If player does not exist, create it."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO players(username) VALUES (%s) ON CONFLICT (username) DO NOTHING",
                (username,)
            )

            cur.execute(
                "SELECT id FROM players WHERE username = %s",
                (username,)
            )

            player_id = cur.fetchone()[0]

        conn.commit()

    return player_id


def save_result(username, score, level):
    """Save game result to database after game over."""
    player_id = get_or_create_player(username)

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO game_sessions(player_id, score, level_reached)
                VALUES (%s, %s, %s)
                """,
                (player_id, score, level)
            )
        conn.commit()


def get_personal_best(username):
    """Get best score of current player."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX(gs.score), 0)
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                WHERE p.username = %s
                """,
                (username,)
            )

            best = cur.fetchone()[0]

    return best


def get_top_scores(limit=10):
    """Get top 10 leaderboard from database."""
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT
                    p.username,
                    gs.score,
                    gs.level_reached,
                    TO_CHAR(gs.played_at, 'YYYY-MM-DD HH24:MI')
                FROM game_sessions gs
                JOIN players p ON gs.player_id = p.id
                ORDER BY gs.score DESC, gs.level_reached DESC, gs.played_at ASC
                LIMIT %s
                """,
                (limit,)
            )

            rows = cur.fetchall()

    return rows