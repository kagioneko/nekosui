"""
ネコスイ MCP サーバー

ChatGPT などの MCP クライアントから猫の状態を操作するためのサーバー。
バックエンド（FastAPI）が起動していなくても動作するよう、
DBを直接参照する。
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Literal

# バックエンドのモジュールを使う
BACKEND_DIR = Path(__file__).parent / "backend"
sys.path.insert(0, str(BACKEND_DIR))

import _paths  # noqa: F401

import asyncio
from mcp.server.fastmcp import FastMCP
from session_manager import get_session_status, create_cat_and_session, update_session, add_chat_log
from cat_initializer import create_new_cat
from cat_event_mapper import get_action_event
from cat_behavior import decide_cat_behavior, decide_can_return
from cat_prompt_builder import build_cat_system_prompt
from llm_client import generate_cat_response, is_llm_enabled
from time_behavior import get_time_period
from recovery_manager import apply_action_recovery_boost
from database import init_db

# 保存済みセッションファイル（バックエンドと共用）
_SAVED_SESSION_FILE = BACKEND_DIR / "saved_session.json"


def _load_session_id() -> str | None:
    if _SAVED_SESSION_FILE.exists():
        data = json.loads(_SAVED_SESSION_FILE.read_text())
        return data.get("session_id")
    return None


def _save_session_id(session_id: str) -> None:
    _SAVED_SESSION_FILE.write_text(json.dumps({"session_id": session_id}))


def _clamp(v: float) -> float:
    return max(0.0, min(100.0, v))


def _apply_delta(neuro: dict, delta: dict) -> dict:
    return {k: _clamp(neuro.get(k, 50.0) + delta.get(k, 0.0)) for k in neuro}


def _neuro_to_description(neuro: dict, personality: str) -> str:
    """NeuroState を自然言語で説明する（ChatGPTが画像生成しやすいように）。"""
    o = neuro.get("O", 50)
    s = neuro.get("S", 50)
    d = neuro.get("D", 50)
    g = neuro.get("G", 50)
    e = neuro.get("E", 50)
    c = neuro.get("C", 50)

    moods = []

    # オキシトシン（愛着・甘え度）
    if o >= 70:
        moods.append("とても甘えたくてごろごろしている")
    elif o >= 50:
        moods.append("まあまあ機嫌がいい")
    elif o >= 30:
        moods.append("少し警戒している")
    else:
        moods.append("距離を置きたがっている")

    # セロトニン（落ち着き）
    if s <= 20:
        moods.append("ピリピリと落ち着きがない")
    elif s >= 70:
        moods.append("とてもリラックスしている")

    # ドーパミン（好奇心・興奮）
    if d >= 70:
        moods.append("目がキラキラして遊びたそう")
    elif d <= 20:
        moods.append("ぐったりして眠そう")

    # グルタミン酸（覚醒）
    if g <= 20:
        moods.append("半分目が閉じている")
    elif g >= 80:
        moods.append("耳をピンと立てて警戒中")

    # エンドルフィン（幸福感）
    if e >= 70:
        moods.append("幸せそうにのびをしている")

    personality_desc = {
        "tsundere": "ツンデレ気質（普段そっけないが内心甘えたい）",
        "amaenbo": "甘えん坊（常にそばにいたい）",
        "maipeesu": "マイペース（我が道を行く）",
    }.get(personality, "気ままな")

    mood_str = "、".join(moods) if moods else "普通の状態"
    return f"{personality_desc}の猫。今の状態: {mood_str}。"


# --- MCP サーバー ---

mcp = FastMCP("nekosui")


@mcp.tool()
async def get_cat_status() -> str:
    """
    今の猫の状態（NeuroState・気分・親密度）を取得する。
    画像生成のプロンプトに使える自然言語の気分説明も含まれる。
    """
    await init_db()
    session_id = _load_session_id()
    if not session_id:
        return "猫がいません。まず setup_cat で猫を作ってください。"

    status = await get_session_status(session_id)
    if not status:
        return "セッションが見つかりません。setup_cat で猫を作り直してください。"

    ns = status.neuro_state
    neuro_dict = {
        "D": ns.D, "S": ns.S, "C": ns.C,
        "O": ns.O, "G": ns.G, "E": ns.E,
        "corruption": ns.corruption,
    }
    mood_desc = _neuro_to_description(neuro_dict, status.cat.personality)
    time_info = get_time_period()

    return json.dumps({
        "cat_name": status.cat.name,
        "personality": status.cat.personality,
        "fur_color": status.cat.fur_color,
        "is_fled": status.is_fled,
        "relationship_level": round(status.relationship_level, 3),
        "time_period": time_info.period,
        "neuro_state": {
            "O_oxytocin": round(ns.O, 1),
            "S_serotonin": round(ns.S, 1),
            "D_dopamine": round(ns.D, 1),
            "G_glutamate": round(ns.G, 1),
            "E_endorphin": round(ns.E, 1),
            "C_cortisol": round(ns.C, 1),
        },
        "mood_description": mood_desc,
        "image_prompt_hint": (
            f"A {status.cat.fur_color} cat, {mood_desc} "
            f"Time of day: {time_info.period}. "
            f"Anime style, cute, detailed."
        ),
    }, ensure_ascii=False, indent=2)


@mcp.tool()
async def setup_cat(
    name: str,
    personality: Literal["tsundere", "amaenbo", "maipeesu"] = "maipeesu",
    fur_color: Literal["しろ", "くろ", "みけ", "キジトラ", "サビ"] = "しろ",
) -> str:
    """
    新しい猫を作る。

    Args:
        name: 猫の名前（例: ミル、そら、きなこ）
        personality: 性格。必ず以下の3つから選ぶこと。
            - "tsundere" … ツンデレ。なかなか懐かないが懐くと急に甘える
            - "amaenbo" … 甘えん坊。すぐ好きになりずっとそばにいたがる
            - "maipeesu" … マイペース。変化が穏やかで我が道を行く（デフォルト）
        fur_color: 毛色。"しろ" / "くろ" / "みけ" / "キジトラ" / "サビ" から選ぶ
    """
    await init_db()
    init_data = create_new_cat(personality)
    cat_id, session_id = await create_cat_and_session(
        name=name,
        personality=personality,
        fur_color=fur_color,
        birthday=init_data.birthday,
        neuro_state=init_data.neuro_state,
    )
    _save_session_id(session_id)

    o = init_data.neuro_state["O"]
    if personality == "tsundere":
        greeting = "…（興味なさそうにこちらを見た）" if o < 30 else "…べつに、気になったわけじゃないから"
    elif personality == "amaenbo":
        greeting = "にゃ〜ん！" if o >= 30 else "…（じっとこちらを見ている）"
    else:
        greeting = "…（ゆっくりこちらに近づいてきた）"

    return f"{name}が来た！\n{greeting}\n\nセッションID: {session_id}"


@mcp.tool()
async def do_action(action: str, text: str = "") -> str:
    """
    猫にアクションをする。
    action: nekosui（猫吸い）/ naderu（なでる）/ gohan（ごはん）/
            asobu（遊ぶ）/ dakko（抱っこ）/ namae（名前を呼ぶ）/
            mushi（無視）/ text（話しかける）
    text: action が text のときの発言内容
    """
    await init_db()
    session_id = _load_session_id()
    if not session_id:
        return "猫がいません。setup_cat で猫を作ってください。"

    status = await get_session_status(session_id)
    if not status:
        return "セッションが見つかりません。"

    cat = status.cat
    neuro_dict = {
        "D": status.neuro_state.D, "S": status.neuro_state.S,
        "C": status.neuro_state.C, "O": status.neuro_state.O,
        "G": status.neuro_state.G, "E": status.neuro_state.E,
        "corruption": status.neuro_state.corruption,
    }
    is_fled = status.is_fled
    consecutive = status.consecutive_nekosui
    relationship = status.relationship_level
    time_info = get_time_period()

    # 逃げてる猫が戻るか
    if is_fled:
        neuro_dict = apply_action_recovery_boost(neuro_dict, action, cat.personality)
        if decide_can_return(neuro_dict):
            is_fled = False
            consecutive = 0

    # アクション実行
    state_event, action_result = get_action_event(
        action=action,
        consecutive_nekosui=consecutive,
        neuro_state=neuro_dict,
        personality=cat.personality,
    )
    delta = state_event.to_delta()
    new_neuro = {k: _clamp(neuro_dict.get(k, 50.0) + delta.get(k, 0.0)) for k in neuro_dict}

    # 連続猫吸いカウント
    if action == "nekosui":
        new_consecutive = 0 if action_result == "flee" else consecutive + 1
    else:
        new_consecutive = 0

    # 逃げ判定
    new_is_fled = is_fled
    if action_result in ("flee", "escape"):
        new_is_fled = True
        new_consecutive = 0

    # 行動決定
    behavior = decide_cat_behavior(
        action_result=action_result,
        action=action,
        neuro_state=new_neuro,
        personality=cat.personality,
        time_info=time_info,
        is_currently_fled=new_is_fled,
    )

    # 親密度更新
    gain_map = {"goro": 0.008, "stare": 0.002, "kick": -0.001,
                "flee": -0.005, "ok": 0.003, "accept": 0.006,
                "resist": 0.001, "escape": -0.002}
    base = gain_map.get(action_result, 0.001)
    if new_neuro["O"] > 60:
        base *= 1.5
    new_relationship = max(0.0, min(1.0, relationship + base))

    # LLM セリフ生成
    action_descs = {
        "nekosui": "飼い主があなたに顔を近づけて猫吸いしてきた",
        "naderu": "飼い主があなたをなでてきた",
        "gohan": "飼い主がごはんをくれた",
        "asobu": "飼い主があなたと遊ぼうとしている",
        "dakko": "飼い主があなたを抱っこしようとした",
        "namae": "飼い主があなたの名前を呼んだ",
        "mushi": "飼い主がしばらくあなたを無視していた",
        "text": f'飼い主が「{text}」と話しかけてきた' if text else "飼い主が話しかけてきた",
    }
    action_desc = action_descs.get(action, "飼い主が何かした")
    system_prompt = build_cat_system_prompt(
        cat_name=cat.name, personality=cat.personality,
        time_info=time_info, neuro_state=new_neuro,
        relationship_level=new_relationship, is_fled=new_is_fled,
    )
    final_message = await generate_cat_response(
        system_prompt=system_prompt,
        user_action=action_desc,
        fallback_message=behavior.message,
    )

    # DB 更新
    await update_session(
        session_id=session_id, neuro_state=new_neuro,
        relationship_level=new_relationship,
        is_fled=new_is_fled, consecutive_nekosui=new_consecutive,
    )
    await add_chat_log(session_id, "user", action, text or action)
    await add_chat_log(session_id, "cat", None, final_message, behavior.pose, behavior.expression)

    mood_desc = _neuro_to_description(new_neuro, cat.personality)

    return json.dumps({
        "cat_name": cat.name,
        "action": action,
        "result": action_result,
        "message": final_message,
        "pose": behavior.pose,
        "expression": behavior.expression,
        "is_fled": new_is_fled,
        "relationship_level": round(new_relationship, 3),
        "mood_after": mood_desc,
        "image_prompt_hint": (
            f"A {cat.fur_color} cat, {mood_desc} "
            f"Pose: {behavior.pose}, expression: {behavior.expression}. "
            f"Anime style, cute, detailed."
        ),
    }, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    mcp.run()
