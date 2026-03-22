"""NeuroState → 猫の行動決定モジュール

NeuroStateと時間帯・性格から猫の具体的な挙動を決定する。
Phase 1（LLMなし）: 固定テンプレート応答を返す。
"""

from __future__ import annotations
import random
from dataclasses import dataclass

from models import PersonalityType
from time_behavior import TimePeriodInfo


# --- 立ち絵キー定義 ---
# ポーズ: sit / lie / curl / stand / nuzzle / groom
# 表情: normal / happy / annoyed

@dataclass
class BehaviorDecision:
    """猫の挙動決定結果"""
    message: str       # 猫のセリフ（空文字 = 無視）
    pose: str          # 立ち絵ポーズキー
    expression: str    # 立ち絵表情キー
    sound: str | None  # 効果音キー
    is_flee: bool      # このアクションで逃げるか


# --- セリフテンプレート ---

_TEMPLATES: dict[str, dict[str, list[str]]] = {
    # action_result → personality → セリフリスト
    "goro": {
        "tsundere": ["…べつに、嫌いじゃないから", "…もういいよ", "ふん、好きにしろ"],
        "amaenbo": ["にゃ〜ん♪", "もっと吸って〜", "ごろごろ〜"],
        "maipace": ["…", "ごろ", "ふむ"],
    },
    "stare": {
        "tsundere": ["…なに", "ちょっと、やめてよ", "…（じっと）"],
        "amaenbo": ["ん〜？", "もうちょっと待って", "…（迷い中）"],
        "maipace": ["…（じっと見る）", "ふむ", "…"],
    },
    "punch": {
        "tsundere": ["ぺしっ", "…（無言でぱんち）", "触るな", "…（じろり）ぺし"],
        "amaenbo": ["や！", "ぺしっ…（でもまだいる）", "ちょっと！"],
        "maipace": ["…（ぺし）", "やめ", "…（無言でぱんち）"],
    },
    "kick": {
        "tsundere": ["ふしゃー！", "触るな！", "やめろって言ってる！"],
        "amaenbo": ["や、やだ！", "いたい！", "ふー！"],
        "maipace": ["……", "やめ", "（足蹴り）"],
    },
    "hiss": {
        "tsundere": ["ふしゃーっ！！", "来るな！！", "近づくな！"],
        "amaenbo": ["いや〜！！", "やめて〜！！"],
        "maipace": ["…シャー", "…（威嚇）"],
    },
    "naderu_punch": {
        "tsundere": ["ぺしっ…（じろり）", "…やめろ", "触りすぎ"],
        "amaenbo": ["も、もうちょっとだけ…ぺし", "や！（でも逃げない）"],
        "maipace": ["…（ぺし）", "やめ", "限界"],
    },
    "naderu_kick": {
        "tsundere": ["いい加減にしろ！", "触るな！", "ふしゃっ！"],
        "amaenbo": ["やだやだ！", "もうやだ！ふー！"],
        "maipace": ["…（足蹴り）", "やめ", "……"],
    },
    "flee": {
        "tsundere": ["うるさい！もう知らない！", "あっち行って！"],
        "amaenbo": ["もうやだ〜！", "ひどい〜！"],
        "maipace": ["…（去っていく）"],
    },
    "naderu_ok": {
        "tsundere": ["…（目を細める）", "べつに嫌じゃない", "…ふん"],
        "amaenbo": ["にゃ〜ん♪", "もっとなでて！", "好き好き〜！"],
        "maipace": ["ごろ", "…（うっとり）", "ふむ"],
    },
    "gohan_ok": {
        "tsundere": ["…ちょうどよかった", "べつに待ってたわけじゃない"],
        "amaenbo": ["やった〜！ごはん！", "ありがとにゃ〜！"],
        "maipace": ["ふむ", "ごはん", "…（食べる）"],
    },
    "asobu_ok": {
        "tsundere": ["…（しぶしぶ）ちょっとだけ", "一緒に遊ぶとか言ってない"],
        "amaenbo": ["やった〜！あそぼ〜！", "もっとやろ〜！"],
        "maipace": ["…（ちょっと動く）", "ふむ", "まあ、いいか"],
    },
    "dakko_accept": {
        "tsundere": ["…（しぶしぶ）", "重いって言うなよ", "ちょっとだけ"],
        "amaenbo": ["きゃ〜！だっこ〜！", "ずっとこのままで〜！"],
        "maipace": ["…（おとなしくしてる）", "ふむ"],
    },
    "dakko_resist": {
        "tsundere": ["やめろ！", "触るな！", "近寄るな！"],
        "amaenbo": ["や〜！", "今はやだ！"],
        "maipace": ["…（嫌そう）", "やめて"],
    },
    "dakko_escape": {
        "tsundere": ["ふしゃー！！", "近づくな！！"],
        "amaenbo": ["いや〜！", "やめて〜！"],
        "maipace": ["…（逃げた）"],
    },
    "namae_ok": {
        "tsundere": ["…なに", "呼んだ？", "…（ちらっと見る）"],
        "amaenbo": ["な〜に〜？", "はーい！", "なに！？なに！？"],
        "maipace": ["…", "ふむ", "…（見る）"],
    },
    "mushi_ok": {
        "tsundere": ["…（無視）", "（毛づくろい中）"],
        "amaenbo": ["ねえ〜、見て〜", "かまって〜"],
        "maipace": ["…", "…（寝てる）"],
    },
    "text_ok": {
        "tsundere": ["…（じっと見る）", "…", "にゃ"],
        "amaenbo": ["にゃ〜？", "なに〜？", "にゃんにゃん"],
        "maipace": ["…", "にゃ", "ふむ"],
    },
    "midnight_ignore": {
        "tsundere": ["…（寝てる）"],
        "amaenbo": ["…（寝てる）"],
        "maipace": ["…（深夜なので）"],
    },
    "return": {
        "tsundere": ["……戻ってきた。べつに、寂しかったわけじゃないから"],
        "amaenbo": ["ただいま〜……（ふりふり）"],
        "maipace": ["…（戻ってきた）"],
    },
}

# 逃げてる間のメッセージ
_FLED_MESSAGE: dict[PersonalityType, str] = {
    "tsundere": "（どこかへ行ってしまった……）",
    "amaenbo":  "（拗ねて部屋の隅に隠れた……）",
    "maipace":  "（いなくなった……）",
}


def _pick(template_key: str, personality: PersonalityType) -> str:
    """テンプレートからランダムにセリフを選ぶ。"""
    options = _TEMPLATES.get(template_key, {}).get(personality, ["…"])
    return random.choice(options)


def decide_pose_expression(
    o: float,
    d: float,
    g: float,
    time_period: str,
    is_fled: bool,
) -> tuple[str, str]:
    """NeuroStateから立ち絵のポーズと表情を決定する。"""
    if is_fled:
        return "curl", "normal"

    if time_period == "midnight" and g > 55:
        return "curl", "normal"  # 深夜・眠い

    if d > 70:
        return "stand", "happy"  # 興奮
    elif o > 65:
        return "nuzzle", "happy"  # 甘え
    elif g > 60 and d < 40:
        return "lie", "normal"   # まったり
    elif o < 20:
        return "groom", "annoyed"  # 不機嫌
    else:
        return "sit", "normal"   # デフォルト


def decide_cat_behavior(
    action_result: str,
    action: str,
    neuro_state: dict[str, float],
    personality: PersonalityType,
    time_info: TimePeriodInfo,
    is_currently_fled: bool,
) -> BehaviorDecision:
    """アクション結果とNeuroStateから猫の行動を決定する。

    Args:
        action_result: cat_event_mapperが返した結果ラベル
        action: ユーザーのアクション種別
        neuro_state: 更新後のNeuroState dict
        personality: 猫の性格
        time_info: 現在の時間帯情報
        is_currently_fled: 逃げ中かどうか

    Returns:
        BehaviorDecision
    """
    o = neuro_state.get("O", 20.0)
    d = neuro_state.get("D", 50.0)
    g = neuro_state.get("G", 50.0)

    # --- 逃げてる状態 ---
    if is_currently_fled:
        pose, expr = decide_pose_expression(o, d, g, time_info.period, True)
        return BehaviorDecision(
            message=_FLED_MESSAGE[personality],
            pose=pose,
            expression=expr,
            sound=None,
            is_flee=False,
        )

    # --- 深夜ほぼ無視 ---
    if time_info.period == "midnight" and random.random() > time_info.response_rate:
        pose, expr = decide_pose_expression(o, d, g, time_info.period, False)
        return BehaviorDecision(
            message=_pick("midnight_ignore", personality),
            pose="curl",
            expression="normal",
            sound=None,
            is_flee=False,
        )

    # --- action_result → セリフ・演出 ---
    is_flee = action_result == "flee"

    template_key = _get_template_key(action, action_result)
    message = _pick(template_key, personality)

    if is_flee:
        pose, expr = "sit", "annoyed"
        sound = "hissing"
    else:
        pose, expr = decide_pose_expression(o, d, g, time_info.period, False)
        sound = _get_sound(action_result, o)

    return BehaviorDecision(
        message=message,
        pose=pose,
        expression=expr,
        sound=sound,
        is_flee=is_flee,
    )


def _get_template_key(action: str, result: str) -> str:
    """アクションと結果からテンプレートキーを生成する。"""
    mapping = {
        ("nekosui", "goro"):   "goro",
        ("nekosui", "stare"):  "stare",
        ("nekosui", "punch"):  "punch",
        ("nekosui", "kick"):   "kick",
        ("nekosui", "flee"):   "flee",
        ("dakko", "accept"):   "dakko_accept",
        ("dakko", "resist"):   "dakko_resist",
        ("dakko", "escape"):   "dakko_escape",
        ("naderu", "ok"):      "naderu_ok",
        ("naderu", "punch"):   "naderu_punch",
        ("naderu", "kick"):    "naderu_kick",
        ("naderu", "hiss"):    "hiss",
        ("gohan", "ok"):       "gohan_ok",
        ("asobu", "ok"):       "asobu_ok",
        ("namae", "ok"):       "namae_ok",
        ("mushi", "ok"):       "mushi_ok",
        ("text", "ok"):        "text_ok",
    }
    return mapping.get((action, result), "text_ok")


def _get_sound(result: str, o: float) -> str | None:
    """結果とOキシトシン値から効果音キーを返す。"""
    sound_map = {
        "goro":   "purring",
        "stare":  None,
        "punch":  "swat",
        "kick":   "hissing",
        "hiss":   "hissing",
        "flee":   "hissing",
        "ok":     "purring" if o >= 55 else None,
        "accept": "purring",
        "resist": None,
        "escape": "hissing",
    }
    return sound_map.get(result)


def decide_can_return(neuro_state: dict[str, float]) -> bool:
    """逃げた猫が戻ってくるか判定する。

    S（セロトニン）とG（GABA）が回復したら確率的に戻ってくる。
    """
    s = neuro_state.get("S", 50.0)
    g = neuro_state.get("G", 50.0)

    if s >= 55 and g >= 50:
        return random.random() < 0.35   # 35%の確率で戻る
    elif s >= 40 and g >= 40:
        return random.random() < 0.10   # 10%
    return False
