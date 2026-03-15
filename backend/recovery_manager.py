"""
逃げた猫の自然回復モジュール

- バックグラウンドタスク: 一定間隔でS・Gを自然回復させる
- アクションブースト: 特定アクションで回復を加速する（性格差あり）
"""

from __future__ import annotations
import asyncio
import logging
from typing import TYPE_CHECKING

import aiosqlite
from database import get_db_path

if TYPE_CHECKING:
    pass

logger = logging.getLogger(__name__)

# バックグラウンド回復の間隔（秒）
RECOVERY_INTERVAL = 180  # 3分ごと

# バックグラウンド自然回復量（逃げ中のセッションのみ）
NATURAL_RECOVERY = {"S": 1.5, "G": 1.0}

# アクション × 性格 → 回復ブースト量（S, G）
# 負の値 = 逆効果（逃げ期間が延びる）
# 逃げ中のときだけ適用される
_ACTION_BOOST: dict[str, dict[str, tuple[float, float]]] = {
    "gohan": {
        "tsundere":  (8.0, 5.0),   # ツンデレも食べ物には弱い
        "amaenbo":   (10.0, 6.0),
        "maipace":   (8.0, 5.0),
    },
    "oyatsu": {
        "tsundere":  (8.0, 5.0),   # おやつも同様
        "amaenbo":   (10.0, 6.0),
        "maipace":   (8.0, 5.0),
    },
    "naderu": {
        "tsundere":  (-2.0, -1.0), # ツンデレ: 追いかけてなでようとするとさらに逃げる
        "amaenbo":   (5.0, 3.0),
        "maipace":   (3.0, 2.0),
    },
    "yobu": {
        "tsundere":  (-1.5, -1.0), # ツンデレ: 呼ばれるとむしろ意地になる
        "amaenbo":   (6.0, 4.0),   # 甘えん坊は名前呼ばれると回復が早い
        "maipace":   (2.5, 2.0),
    },
    "text": {
        "tsundere":  (-1.0, -0.5), # ツンデレ: 話しかけると「うるさい」ってなる
        "amaenbo":   (3.0, 2.0),
        "maipace":   (1.5, 1.0),
    },
    "asobu": {
        "tsundere":  (-1.5, -1.0), # ツンデレ: 遊ぼうとするとさらに距離を置く
        "amaenbo":   (4.0, 2.5),
        "maipace":   (2.0, 1.5),
    },
    "mushi": {
        "tsundere":  (4.0, 3.0),   # ツンデレ: 無視されると気になってくる（ツンデレあるある）
        "amaenbo":   (-3.0, -2.0), # 甘えん坊: 無視されると傷つく
        "maipace":   (1.0, 1.0),   # マイペース: 無視は普通
    },
}


def apply_action_recovery_boost(
    neuro: dict[str, float],
    action: str,
    personality: str,
) -> dict[str, float]:
    """逃げ中に特定アクションを送ったとき、S・Gをブーストする。

    効果がないアクション（猫吸い・抱っこ）は無視される。
    """
    boost = _ACTION_BOOST.get(action, {}).get(personality)
    if boost is None:
        return neuro

    s_boost, g_boost = boost
    new_neuro = dict(neuro)
    new_neuro["S"] = max(0.0, min(100.0, new_neuro["S"] + s_boost))
    new_neuro["G"] = max(0.0, min(100.0, new_neuro["G"] + g_boost))

    logger.debug(
        "[recovery] action=%s personality=%s S+%.1f G+%.1f → S=%.1f G=%.1f",
        action, personality, s_boost, g_boost,
        new_neuro["S"], new_neuro["G"],
    )
    return new_neuro


async def _tick_all_fled_sessions() -> None:
    """逃げ中の全セッションにS・Gの自然回復を適用する。"""
    async with aiosqlite.connect(get_db_path()) as db:
        db.row_factory = aiosqlite.Row
        cursor = await db.execute(
            "SELECT session_id, neuro_S, neuro_G FROM sessions WHERE is_fled = 1"
        )
        rows = await cursor.fetchall()

        for row in rows:
            new_s = min(100.0, row["neuro_S"] + NATURAL_RECOVERY["S"])
            new_g = min(100.0, row["neuro_G"] + NATURAL_RECOVERY["G"])
            await db.execute(
                "UPDATE sessions SET neuro_S=?, neuro_G=? WHERE session_id=?",
                (new_s, new_g, row["session_id"]),
            )
            logger.debug(
                "[recovery] tick session=%s S %.1f→%.1f G %.1f→%.1f",
                row["session_id"], row["neuro_S"], new_s, row["neuro_G"], new_g,
            )

        if rows:
            await db.commit()
            logger.info("[recovery] tick: %d 逃げ中セッションを回復", len(rows))


async def recovery_background_task() -> None:
    """バックグラウンドで定期的に自然回復を走らせるタスク。"""
    logger.info("[recovery] バックグラウンド回復タスク開始（間隔: %d秒）", RECOVERY_INTERVAL)
    while True:
        await asyncio.sleep(RECOVERY_INTERVAL)
        try:
            await _tick_all_fled_sessions()
        except Exception as e:
            logger.error("[recovery] tick エラー: %s", e)
