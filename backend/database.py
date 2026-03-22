"""SQLiteデータベース設定・初期化モジュール"""

from __future__ import annotations
import aiosqlite
from pathlib import Path

DB_PATH = Path(__file__).parent / "nekosui.db"


CREATE_CATS = """
CREATE TABLE IF NOT EXISTS cats (
    cat_id        TEXT PRIMARY KEY,
    name          TEXT NOT NULL,
    personality   TEXT NOT NULL,
    fur_color     TEXT NOT NULL,
    birthday      TEXT NOT NULL,
    created_at    TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

CREATE_SESSIONS = """
CREATE TABLE IF NOT EXISTS sessions (
    session_id          TEXT PRIMARY KEY,
    cat_id              TEXT NOT NULL REFERENCES cats(cat_id),
    neuro_D             REAL NOT NULL DEFAULT 50,
    neuro_S             REAL NOT NULL DEFAULT 50,
    neuro_C             REAL NOT NULL DEFAULT 50,
    neuro_O             REAL NOT NULL DEFAULT 20,
    neuro_G             REAL NOT NULL DEFAULT 50,
    neuro_E             REAL NOT NULL DEFAULT 50,
    neuro_corruption    REAL NOT NULL DEFAULT 0,
    relationship_level  REAL NOT NULL DEFAULT 0.0,
    is_fled             INTEGER NOT NULL DEFAULT 0,
    consecutive_nekosui INTEGER NOT NULL DEFAULT 0,
    consecutive_naderu  INTEGER NOT NULL DEFAULT 0,
    daily_mood          TEXT NOT NULL DEFAULT 'normal',
    daily_mood_date     TEXT NOT NULL DEFAULT '',
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

# 既存DBへのマイグレーション（カラム追加）
_MIGRATIONS = [
    "ALTER TABLE sessions ADD COLUMN consecutive_naderu INTEGER NOT NULL DEFAULT 0",
    "ALTER TABLE sessions ADD COLUMN daily_mood TEXT NOT NULL DEFAULT 'normal'",
    "ALTER TABLE sessions ADD COLUMN daily_mood_date TEXT NOT NULL DEFAULT ''",
]

CREATE_CHAT_HISTORY = """
CREATE TABLE IF NOT EXISTS chat_history (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id  TEXT NOT NULL REFERENCES sessions(session_id),
    role        TEXT NOT NULL,   -- "user" / "cat"
    action      TEXT,
    message     TEXT NOT NULL,
    pose        TEXT,
    expression  TEXT,
    created_at  TEXT NOT NULL DEFAULT (datetime('now'))
)
"""


async def init_db() -> None:
    """データベースを初期化し、マイグレーションを適用する。"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_CATS)
        await db.execute(CREATE_SESSIONS)
        await db.execute(CREATE_CHAT_HISTORY)
        # 既存DBにカラムがなければ追加（エラーは無視）
        for sql in _MIGRATIONS:
            try:
                await db.execute(sql)
            except Exception:
                pass
        await db.commit()


def get_db_path() -> Path:
    """DBファイルパスを返す。"""
    return DB_PATH
