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
    updated_at          TEXT NOT NULL DEFAULT (datetime('now'))
)
"""

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
    """データベースを初期化する（テーブルが存在しない場合のみ作成）。"""
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(CREATE_CATS)
        await db.execute(CREATE_SESSIONS)
        await db.execute(CREATE_CHAT_HISTORY)
        await db.commit()


def get_db_path() -> Path:
    """DBファイルパスを返す。"""
    return DB_PATH
