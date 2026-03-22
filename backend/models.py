"""ネコスイ Pydantic スキーマ定義"""

from __future__ import annotations
from typing import Literal, Optional
from pydantic import BaseModel, Field


# --- 猫の設定 ---

PersonalityType = Literal["tsundere", "amaenbo", "maipace"]
FurColor = Literal["shiro", "kuro", "mike", "kijitora", "sabi"]
DailyMood = Literal["good", "normal", "clingy", "leavemealone", "hunter", "sleepy"]

class CatSetupRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=20, description="猫の名前")
    personality: PersonalityType = "maipace"
    fur_color: FurColor = "mike"


class CatProfile(BaseModel):
    cat_id: str
    name: str
    personality: PersonalityType
    fur_color: FurColor
    birthday: str  # "MM-DD" 形式


# --- NeuroState ---

class NeuroStateView(BaseModel):
    D: float  # Dopamine
    S: float  # Serotonin
    C: float  # Acetylcholine
    O: float  # Oxytocin
    G: float  # GABA
    E: float  # Endorphin
    corruption: float


# --- セッション ---

class SessionStatus(BaseModel):
    session_id: str
    cat: CatProfile
    neuro_state: NeuroStateView
    relationship_level: float  # 0.0 - 1.0
    is_fled: bool  # 逃げてるか
    time_period: str  # "morning" / "midday" / "evening" / "night" / "midnight"
    consecutive_nekosui: int  # 連続猫吸い回数
    consecutive_naderu: int  # 連続なで回数
    daily_mood: str  # 今日の気分


# --- チャット ---

ActionType = Literal[
    "nekosui",   # 猫吸い
    "naderu",    # なでる
    "gohan",     # ごはん
    "asobu",     # 遊ぶ
    "dakko",     # 抱っこ
    "namae",     # 名前を呼ぶ
    "mushi",     # 無視
    "text",      # テキスト入力
]

class ChatRequest(BaseModel):
    session_id: str
    action: ActionType
    text: Optional[str] = None  # action="text" のときのみ使用


class CatResponse(BaseModel):
    message: str                    # 猫のセリフ（空文字 = 無視・無応答）
    pose: str                       # 立ち絵ポーズキー
    expression: str                 # 立ち絵表情キー
    sound: Optional[str]            # 効果音キー
    is_fled: bool                   # 逃げたか
    neuro_state: NeuroStateView
    relationship_level: float
    event_log: list[str]            # デバッグ用イベントログ


# --- セットアップレスポンス ---

class SetupResponse(BaseModel):
    session_id: str
    cat: CatProfile
    initial_state: NeuroStateView
    greeting: str                   # 初日の一言
