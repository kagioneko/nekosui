"""猫の初期NeuroStateランダム化モジュール

性格プリセット別の揺らぎ幅で初期値を生成する。
プレイヤーには見えない「今日の気分」を決定する。
"""

from __future__ import annotations
import random
import math
from datetime import date, datetime
from typing import NamedTuple

from models import PersonalityType


# --- 性格別ベース値 ---

_BASE_STATE: dict[str, float] = {
    "D": 50.0,
    "S": 50.0,
    "C": 50.0,
    "O": 20.0,
    "G": 50.0,
    "E": 50.0,
}

# 性格 × σ（標準偏差）
_SIGMA: dict[PersonalityType, dict[str, float]] = {
    "tsundere": {"D": 15, "S": 20, "C": 10, "O": 5,  "G": 10, "E": 10},
    "amaenbo":  {"D": 10, "S": 15, "C": 8,  "O": 20, "G": 5,  "E": 10},
    "maipace":  {"D": 5,  "S": 5,  "C": 5,  "O": 5,  "G": 5,  "E": 5},
}

# 性格別Oのベース補正（甘えん坊は絆が育ちやすい）
_O_BASE: dict[PersonalityType, float] = {
    "tsundere": 15.0,
    "amaenbo":  30.0,
    "maipace":  20.0,
}


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _gaussian(mu: float, sigma: float) -> float:
    return random.gauss(mu, sigma)


def generate_initial_neuro_state(
    personality: PersonalityType,
    cat_birthday: str,
    rng_seed: int | None = None,
) -> dict[str, float]:
    """性格プリセットと今日の日付に応じた初期NeuroStateを生成する。

    Args:
        personality: 性格プリセット
        cat_birthday: "MM-DD" 形式の誕生日
        rng_seed: テスト用シード（None = ランダム）

    Returns:
        NeuroState dict {"D": ..., "S": ..., ...}
    """
    if rng_seed is not None:
        random.seed(rng_seed)

    sigmas = _SIGMA[personality]
    state: dict[str, float] = {}

    base = dict(_BASE_STATE)
    base["O"] = _O_BASE[personality]

    for key in ["D", "S", "C", "O", "G", "E"]:
        value = _gaussian(base[key], sigmas[key])
        state[key] = _clamp(value)

    # --- 曜日による微揺らぎ ---
    weekday = datetime.now().weekday()  # 0=月, 4=金
    if weekday == 0:   # 月曜: S微減（猫も月曜嫌い）
        state["S"] = _clamp(state["S"] - random.uniform(3, 8))
    elif weekday == 4:  # 金曜: D微増
        state["D"] = _clamp(state["D"] + random.uniform(3, 8))

    # --- 誕生日ボーナス ---
    today = date.today().strftime("%m-%d")
    if today == cat_birthday:
        state["D"] = _clamp(state["D"] + random.uniform(20, 35))
        state["E"] = _clamp(state["E"] + random.uniform(20, 35))

    state["corruption"] = 0.0
    return state


def generate_birthday() -> str:
    """誕生日をランダム生成する。"MM-DD" 形式で返す。"""
    month = random.randint(1, 12)
    # 月ごとの最大日数（うるう年考慮なし）
    max_days = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    day = random.randint(1, max_days[month])
    return f"{month:02d}-{day:02d}"


class InitialCatData(NamedTuple):
    neuro_state: dict[str, float]
    birthday: str


def create_new_cat(
    personality: PersonalityType,
    rng_seed: int | None = None,
) -> InitialCatData:
    """新しい猫を作成し、初期状態と誕生日を返す。"""
    birthday = generate_birthday()
    neuro_state = generate_initial_neuro_state(personality, birthday, rng_seed)
    return InitialCatData(neuro_state=neuro_state, birthday=birthday)
