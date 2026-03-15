"""セッション・猫データの CRUD モジュール"""

from __future__ import annotations
import uuid
from datetime import datetime

import aiosqlite

from models import (
    CatProfile,
    NeuroStateView,
    SessionStatus,
    PersonalityType,
    FurColor,
)
from database import get_db_path


async def create_cat_and_session(
    name: str,
    personality: PersonalityType,
    fur_color: FurColor,
    birthday: str,
    neuro_state: dict[str, float],
) -> tuple[str, str]:
    """猫とセッションをDBに保存する。

    Returns:
        (cat_id, session_id)
    """
    cat_id = str(uuid.uuid4())
    session_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute(
            "INSERT INTO cats(cat_id, name, personality, fur_color, birthday, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (cat_id, name, personality, fur_color, birthday, now),
        )
        await db.execute(
            "INSERT INTO sessions("
            "  session_id, cat_id, "
            "  neuro_D, neuro_S, neuro_C, neuro_O, neuro_G, neuro_E, neuro_corruption, "
            "  relationship_level, is_fled, consecutive_nekosui, updated_at"
            ") VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 0.0, 0, 0, ?)",
            (
                session_id, cat_id,
                neuro_state["D"], neuro_state["S"], neuro_state["C"],
                neuro_state["O"], neuro_state["G"], neuro_state["E"],
                neuro_state.get("corruption", 0.0),
                now,
            ),
        )
        await db.commit()

    return cat_id, session_id


async def get_session_status(session_id: str) -> SessionStatus | None:
    """セッションの現在状態を取得する。"""
    from time_behavior import get_time_period

    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            """
            SELECT s.*, c.name, c.personality, c.fur_color, c.birthday
            FROM sessions s
            JOIN cats c ON s.cat_id = c.cat_id
            WHERE s.session_id = ?
            """,
            (session_id,),
        )
        row = await cursor.fetchone()

    if row is None:
        return None

    r = row
    time_info = get_time_period()

    cat = CatProfile(
        cat_id=r["cat_id"],
        name=r["name"],
        personality=r["personality"],
        fur_color=r["fur_color"],
        birthday=r["birthday"],
    )
    neuro = NeuroStateView(
        D=r["neuro_D"], S=r["neuro_S"], C=r["neuro_C"],
        O=r["neuro_O"], G=r["neuro_G"], E=r["neuro_E"],
        corruption=r["neuro_corruption"],
    )

    return SessionStatus(
        session_id=session_id,
        cat=cat,
        neuro_state=neuro,
        relationship_level=r["relationship_level"],
        is_fled=bool(r["is_fled"]),
        time_period=time_info.period,
        consecutive_nekosui=r["consecutive_nekosui"],
    )


async def update_session(
    session_id: str,
    neuro_state: dict[str, float],
    relationship_level: float,
    is_fled: bool,
    consecutive_nekosui: int,
) -> None:
    """セッションのNeuroStateと状態を更新する。"""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute(
            """
            UPDATE sessions SET
                neuro_D=?, neuro_S=?, neuro_C=?, neuro_O=?, neuro_G=?, neuro_E=?,
                neuro_corruption=?, relationship_level=?, is_fled=?,
                consecutive_nekosui=?, updated_at=?
            WHERE session_id=?
            """,
            (
                neuro_state["D"], neuro_state["S"], neuro_state["C"],
                neuro_state["O"], neuro_state["G"], neuro_state["E"],
                neuro_state.get("corruption", 0.0),
                relationship_level,
                1 if is_fled else 0,
                consecutive_nekosui,
                now,
                session_id,
            ),
        )
        await db.commit()


async def add_chat_log(
    session_id: str,
    role: str,
    action: str | None,
    message: str,
    pose: str | None = None,
    expression: str | None = None,
) -> None:
    """チャット履歴をDBに追記する。"""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute(
            "INSERT INTO chat_history(session_id, role, action, message, pose, expression, created_at) "
            "VALUES (?, ?, ?, ?, ?, ?, ?)",
            (session_id, role, action, message, pose, expression, now),
        )
        await db.commit()


async def reset_session(session_id: str, new_neuro: dict[str, float]) -> None:
    """セッションをリセットする（猫は残し、NeuroStateだけ初期化）。"""
    now = datetime.utcnow().isoformat()

    async with aiosqlite.connect(get_db_path()) as db:
        await db.execute(
            """
            UPDATE sessions SET
                neuro_D=?, neuro_S=?, neuro_C=?, neuro_O=?, neuro_G=?, neuro_E=?,
                neuro_corruption=0, is_fled=0, consecutive_nekosui=0, updated_at=?
            WHERE session_id=?
            """,
            (
                new_neuro["D"], new_neuro["S"], new_neuro["C"],
                new_neuro["O"], new_neuro["G"], new_neuro["E"],
                now, session_id,
            ),
        )
        await db.commit()
