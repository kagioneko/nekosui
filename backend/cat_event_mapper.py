"""アクション → NeuroState イベント変換モジュール

各アクションがNeuroStateに与えるdelta値を定義する。
猫吸い連続回数はセッション側で管理し、連続回数に応じてdeltaを変化させる。
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Literal

from models import ActionType, PersonalityType


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


# --- 基本アクションイベント定義 ---

_BASE_EVENTS: dict[str, StateEvent] = {
    "naderu":  StateEvent(O=+8, S=+5, E=+3),
    "gohan":   StateEvent(D=+15, E=+5, S=+3),
    "asobu":   StateEvent(D=+10, E=+8, C=+5),
    "namae":   StateEvent(O=+3),
    "mushi":   StateEvent(S=-5, O=-3),
    "text":    StateEvent(O=+2),
}

# 猫吸い: 連続回数 × Oxtocin状態によって変わるため個別関数で計算
# 抱っこ: 性格によって大きく異なるため個別関数で計算


def get_nekosui_event(
    consecutive: int,
    o_level: float,
    personality: PersonalityType,
) -> tuple[StateEvent, str]:
    """猫吸いイベントを計算する。

    Args:
        consecutive: 連続猫吸い回数（0スタート → 今回が何回目か）
        o_level: 現在のOxytocin値
        personality: 猫の性格

    Returns:
        (StateEvent, 結果ラベル)
        結果ラベル: "goro" / "stare" / "kick" / "flee"
    """
    # 連続回数によるストレス蓄積
    stress_map = {0: 0.0, 1: 3.0, 2: 8.0, 3: 15.0}
    base_stress = stress_map.get(consecutive, 20.0)

    # ツンデレはOが上がりにくい → 基本O低め補正
    o_threshold_adj = -10 if personality == "tsundere" else 0

    effective_o = o_level + o_threshold_adj

    if consecutive >= 3:
        # 4回目以上 → 必ず逃げる
        return StateEvent(O=-5, stress=20.0), "flee"
    elif effective_o >= 60:
        return StateEvent(O=+5, E=+5, stress=base_stress), "goro"
    elif effective_o >= 40:
        return StateEvent(O=+1, stress=base_stress + 3), "stare"
    elif effective_o >= 20:
        return StateEvent(O=-3, stress=base_stress + 8), "kick"
    else:
        return StateEvent(O=-5, stress=base_stress + 15), "flee"


def get_dakko_event(
    o_level: float,
    personality: PersonalityType,
) -> tuple[StateEvent, str]:
    """抱っこイベントを計算する。

    Returns:
        (StateEvent, 結果ラベル)
        結果ラベル: "accept" / "resist" / "escape"
    """
    if personality == "tsundere":
        # ツンデレはOが非常に高くないと拒否
        if o_level >= 70:
            return StateEvent(O=+5, E=+3, stress=5.0), "accept"
        elif o_level >= 45:
            return StateEvent(stress=8.0), "resist"
        else:
            return StateEvent(O=-3, stress=15.0), "escape"
    elif personality == "amaenbo":
        # 甘えん坊は抱っこ大好き
        if o_level >= 30:
            return StateEvent(O=+8, E=+8, S=+3), "accept"
        else:
            return StateEvent(O=+3, stress=3.0), "resist"
    else:
        # マイペース: まあまあ許容
        if o_level >= 50:
            return StateEvent(O=+5, E=+3), "accept"
        elif o_level >= 25:
            return StateEvent(stress=5.0), "resist"
        else:
            return StateEvent(stress=10.0), "escape"


def get_action_event(
    action: ActionType,
    consecutive_nekosui: int,
    neuro_state: dict[str, float],
    personality: PersonalityType,
) -> tuple[StateEvent, str]:
    """アクションからStateEventと結果ラベルを返す。

    Args:
        action: ユーザーのアクション
        consecutive_nekosui: 現在の連続猫吸い回数（このアクション実行前）
        neuro_state: 現在のNeuroState dict
        personality: 猫の性格

    Returns:
        (StateEvent, 結果ラベル)
    """
    o = neuro_state.get("O", 20.0)

    if action == "nekosui":
        return get_nekosui_event(consecutive_nekosui, o, personality)
    elif action == "dakko":
        return get_dakko_event(o, personality)
    else:
        base = _BASE_EVENTS.get(action, StateEvent())
        return base, "ok"
