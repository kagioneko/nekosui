"""時間帯判定・時間帯別挙動パターンモジュール"""

from __future__ import annotations
from datetime import datetime
from typing import NamedTuple


class TimePeriodInfo(NamedTuple):
    period: str         # "morning" / "midday" / "evening" / "night" / "midnight"
    label: str          # 日本語ラベル
    response_rate: float  # 返事する確率の基本係数（0.0 - 1.0）
    d_mod: float        # Dopamine 補正値（+/-）
    s_mod: float        # Serotonin 補正値（+/-）
    background: str     # 背景グラデーションキー


_PERIODS: list[tuple[int, int, TimePeriodInfo]] = [
    (6, 10, TimePeriodInfo(
        period="morning", label="朝",
        response_rate=0.85,
        d_mod=+5.0, s_mod=+3.0,
        background="morning",
    )),
    (10, 16, TimePeriodInfo(
        period="midday", label="昼",
        response_rate=0.5,
        d_mod=-3.0, s_mod=0.0,
        background="midday",
    )),
    (16, 20, TimePeriodInfo(
        period="evening", label="夕方",
        response_rate=0.9,
        d_mod=+8.0, s_mod=+2.0,
        background="evening",
    )),
    (20, 24, TimePeriodInfo(
        period="night", label="夜",
        response_rate=0.95,
        d_mod=+2.0, s_mod=+5.0,
        background="night",
    )),
    (0, 6, TimePeriodInfo(
        period="midnight", label="深夜",
        response_rate=0.15,
        d_mod=-5.0, s_mod=-3.0,
        background="midnight",
    )),
]


def get_time_period(now: datetime | None = None) -> TimePeriodInfo:
    """現在時刻に対応する時間帯情報を返す。"""
    if now is None:
        now = datetime.now()

    hour = now.hour
    for start, end, info in _PERIODS:
        if start <= hour < end:
            return info

    # フォールバック（通常到達しない）
    return _PERIODS[-1][2]  # midnight
