"""アクション → NeuroState イベント変換モジュール

各アクションがNeuroStateに与えるdelta値を定義する。
- 猫吸い連続回数・なで連続回数はセッション側で管理
- 今日の気分（daily_mood）と S値でwhim（気まぐれ）確率が変化
"""

from __future__ import annotations
import random
from dataclasses import dataclass
from typing import Literal

from models import ActionType, PersonalityType, DailyMood


@dataclass(frozen=True)
class StateEvent:
    """NeuroState への変化量を表す"""
    D: float = 0.0
    S: float = 0.0
    C: float = 0.0
    O: float = 0.0
    G: float = 0.0
    E: float = 0.0
    stress: float = 0.0   # ストレス（= S低下 + G低下の合計効果）

    def to_delta(self) -> dict[str, float]:
        return {
            "D": self.D,
            "S": self.S - self.stress * 0.6,
            "C": self.C,
            "O": self.O,
            "G": self.G - self.stress * 0.4,
            "E": self.E,
        }


# --- なでる以外の基本アクションイベント ---

_BASE_EVENTS: dict[str, StateEvent] = {
    "gohan":  StateEvent(D=+15, E=+5, S=+3),
    "asobu":  StateEvent(D=+10, E=+8, C=+5),
    "namae":  StateEvent(O=+3),
    "mushi":  StateEvent(S=-5, O=-3),
    "text":   StateEvent(O=+2),
}

# --- 気まぐれ確率モディファイア ---

_MOOD_WHIM_MULT: dict[str, float] = {
    "good":         0.2,
    "normal":       1.0,
    "clingy":       0.4,
    "leavemealone": 3.0,
    "hunter":       1.8,
    "sleepy":       0.6,
}

_PERSONALITY_WHIM_MULT: dict[str, float] = {
    "tsundere": 1.5,
    "amaenbo":  0.5,
    "maipace":  0.9,
}


def apply_mood_whim(
    result: str,
    ladder: list[str],
    neuro_state: dict[str, float],
    personality: str,
    daily_mood: str,
) -> str:
    """気まぐれで結果をワンランク落とす。

    S（セロトニン）が低いほど、leavemealone日ほど確率が上がる。
    """
    if result not in ladder:
        return result
    idx = ladder.index(result)
    if idx >= len(ladder) - 1:
        return result  # 既に最悪結果

    s = neuro_state.get("S", 50.0)
    base_chance = max(0.0, (50.0 - s) / 200.0)  # S=50→0%, S=0→25%
    mood_mult = _MOOD_WHIM_MULT.get(daily_mood, 1.0)
    pers_mult = _PERSONALITY_WHIM_MULT.get(personality, 1.0)

    whim_chance = min(0.6, base_chance * mood_mult * pers_mult)
    if random.random() < whim_chance:
        return ladder[idx + 1]
    return result


# --- 猫吸いイベント ---

# 結果ラベルの段階（punch を stare と kick の間に追加）
_NEKOSUI_LADDER = ["goro", "stare", "punch", "kick", "flee"]


def get_nekosui_event(
    consecutive: int,
    o_level: float,
    personality: PersonalityType,
    neuro_state: dict[str, float],
    daily_mood: str,
) -> tuple[StateEvent, str]:
    """猫吸いイベントを計算する。"""
    stress_map = {0: 0.0, 1: 3.0, 2: 8.0, 3: 15.0}
    base_stress = stress_map.get(consecutive, 20.0)

    o_threshold_adj = -10 if personality == "tsundere" else 0
    effective_o = o_level + o_threshold_adj

    if consecutive >= 3:
        return StateEvent(O=-5, stress=20.0), "flee"
    elif effective_o >= 60:
        base_result = "goro"
        event = StateEvent(O=+5, E=+5, stress=base_stress)
    elif effective_o >= 40:
        base_result = "stare"
        event = StateEvent(O=+1, stress=base_stress + 3)
    elif effective_o >= 20:
        base_result = "punch"
        event = StateEvent(O=-2, stress=base_stress + 5)
    else:
        base_result = "kick"
        event = StateEvent(O=-4, stress=base_stress + 10)

    # 気まぐれで結果を悪化させる可能性
    final_result = apply_mood_whim(base_result, _NEKOSUI_LADDER, neuro_state, personality, daily_mood)
    return event, final_result


# --- なでるイベント ---

# なで連続回数の閾値: (punch開始, kick開始, hiss開始) ← daily_moodで変動
_NADERU_THRESHOLDS: dict[str, tuple[int, int, int]] = {
    "good":         (4, 7, 10),
    "normal":       (3, 5, 7),
    "clingy":       (4, 6, 9),
    "leavemealone": (0, 2, 4),   # 最初からpunchあり・すぐhiss
    "hunter":       (2, 4, 6),
    "sleepy":       (3, 5, 7),
}

_NADERU_LADDER = ["ok", "punch", "kick", "hiss"]


def get_naderu_event(
    consecutive: int,
    daily_mood: str,
    personality: PersonalityType,
    neuro_state: dict[str, float],
) -> tuple[StateEvent, str]:
    """なでるイベントを計算する。

    Args:
        consecutive: 連続なで回数（0スタート → 今回が何回目か）
        daily_mood: 今日の気分
        personality: 猫の性格
        neuro_state: 現在のNeuroState

    Returns:
        (StateEvent, 結果ラベル: "ok" / "punch" / "kick" / "hiss")
        ※ hiss は flee と同じく逃走扱い
    """
    punch_at, kick_at, hiss_at = _NADERU_THRESHOLDS.get(daily_mood, (3, 5, 7))

    if consecutive >= hiss_at:
        base_result = "hiss"
        event = StateEvent(O=-5, stress=15.0)
    elif consecutive >= kick_at:
        base_result = "kick"
        event = StateEvent(O=-3, stress=8.0)
    elif consecutive >= punch_at:
        base_result = "punch"
        event = StateEvent(O=-1, stress=3.0)
    else:
        base_result = "ok"
        event = StateEvent(O=+8, S=+5, E=+3)

    # ok の時も気まぐれで悪化する可能性
    final_result = apply_mood_whim(base_result, _NADERU_LADDER, neuro_state, personality, daily_mood)
    return event, final_result


# --- 抱っこイベント ---

def get_dakko_event(
    o_level: float,
    personality: PersonalityType,
) -> tuple[StateEvent, str]:
    """抱っこイベントを計算する。"""
    if personality == "tsundere":
        if o_level >= 70:
            return StateEvent(O=+5, E=+3, stress=5.0), "accept"
        elif o_level >= 45:
            return StateEvent(stress=8.0), "resist"
        else:
            return StateEvent(O=-3, stress=15.0), "escape"
    elif personality == "amaenbo":
        if o_level >= 30:
            return StateEvent(O=+8, E=+8, S=+3), "accept"
        else:
            return StateEvent(O=+3, stress=3.0), "resist"
    else:
        if o_level >= 50:
            return StateEvent(O=+5, E=+3), "accept"
        elif o_level >= 25:
            return StateEvent(stress=5.0), "resist"
        else:
            return StateEvent(stress=10.0), "escape"


# --- メイン呼び出し ---

def get_action_event(
    action: ActionType,
    consecutive_nekosui: int,
    consecutive_naderu: int,
    neuro_state: dict[str, float],
    personality: PersonalityType,
    daily_mood: str = "normal",
) -> tuple[StateEvent, str]:
    """アクションからStateEventと結果ラベルを返す。"""
    o = neuro_state.get("O", 20.0)

    if action == "nekosui":
        return get_nekosui_event(consecutive_nekosui, o, personality, neuro_state, daily_mood)
    elif action == "naderu":
        return get_naderu_event(consecutive_naderu, daily_mood, personality, neuro_state)
    elif action == "dakko":
        return get_dakko_event(o, personality)
    else:
        base = _BASE_EVENTS.get(action, StateEvent())
        return base, "ok"
