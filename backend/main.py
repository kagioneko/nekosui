"""ネコスイ バックエンド FastAPI アプリ"""

from __future__ import annotations
import asyncio
import sys
from pathlib import Path

# .env を読み込む（python-dotenv があれば）
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass

# 依存リポジトリをsys.pathに追加
sys.path.insert(0, str(Path(__file__).parent))
import _paths  # noqa: F401

from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from models import (
    CatSetupRequest,
    ChatRequest,
    CatResponse,
    SetupResponse,
    SessionStatus,
    NeuroStateView,
)
from database import init_db
from cat_initializer import create_new_cat
from cat_event_mapper import get_action_event
from cat_behavior import decide_cat_behavior, decide_can_return, BehaviorDecision
from cat_prompt_builder import build_cat_system_prompt
from llm_client import generate_cat_response, is_llm_enabled, active_provider
from session_manager import (
    create_cat_and_session,
    get_session_status,
    update_session,
    add_chat_log,
    reset_session,
)
from time_behavior import get_time_period
from recovery_manager import apply_action_recovery_boost, recovery_background_task

# 保存済みセッションファイル
_SAVED_SESSION_FILE = Path(__file__).parent / "saved_session.json"

def _load_saved_session() -> str | None:
    if _SAVED_SESSION_FILE.exists():
        import json
        data = json.loads(_SAVED_SESSION_FILE.read_text())
        return data.get("session_id")
    return None

def _save_session(session_id: str) -> None:
    import json
    _SAVED_SESSION_FILE.write_text(json.dumps({"session_id": session_id}))

def _clear_saved_session() -> None:
    if _SAVED_SESSION_FILE.exists():
        _SAVED_SESSION_FILE.unlink()


# --- NeuroState 更新ユーティリティ ---

def _clamp(v: float) -> float:
    return max(0.0, min(100.0, v))


def apply_state_delta(
    neuro: dict[str, float],
    delta: dict[str, float],
) -> dict[str, float]:
    """NeuroStateにdeltaを適用し、clampして返す。"""
    return {
        "D": _clamp(neuro.get("D", 50.0) + delta.get("D", 0.0)),
        "S": _clamp(neuro.get("S", 50.0) + delta.get("S", 0.0)),
        "C": _clamp(neuro.get("C", 50.0) + delta.get("C", 0.0)),
        "O": _clamp(neuro.get("O", 20.0) + delta.get("O", 0.0)),
        "G": _clamp(neuro.get("G", 50.0) + delta.get("G", 0.0)),
        "E": _clamp(neuro.get("E", 50.0) + delta.get("E", 0.0)),
        "corruption": _clamp(neuro.get("corruption", 0.0) + delta.get("corruption", 0.0)),
    }


def _neuro_dict_to_view(nd: dict[str, float]) -> NeuroStateView:
    return NeuroStateView(
        D=nd["D"], S=nd["S"], C=nd["C"],
        O=nd["O"], G=nd["G"], E=nd["E"],
        corruption=nd.get("corruption", 0.0),
    )


_ACTION_DESC: dict[str, str] = {
    "nekosui": "飼い主があなたに顔を近づけて猫吸いしてきた",
    "naderu":  "飼い主があなたをなでてきた",
    "gohan":   "飼い主がごはんをくれた",
    "asobu":   "飼い主があなたと遊ぼうとしている",
    "dakko":   "飼い主があなたを抱っこしようとした",
    "namae":   "飼い主があなたの名前を呼んだ",
    "mushi":   "飼い主がしばらくあなたを無視していた",
    "text":    "飼い主が話しかけてきた",
}


def _action_to_desc(action: str, text: str | None) -> str:
    base = _ACTION_DESC.get(action, "飼い主が何かした")
    if action == "text" and text:
        return f'飼い主が「{text}」と話しかけてきた'
    return base


def compute_relationship_gain(action_result: str, o: float) -> float:
    """アクション結果とOキシトシン値から親密度上昇量を計算する。"""
    gain_map = {
        "goro": 0.008,
        "stare": 0.002,
        "kick": -0.001,
        "flee": -0.005,
        "ok": 0.003,
        "accept": 0.006,
        "resist": 0.001,
        "escape": -0.002,
    }
    base = gain_map.get(action_result, 0.001)
    if o > 60:
        base *= 1.5
    return base


# --- アプリ起動/終了 ---

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    task = asyncio.create_task(recovery_background_task())
    yield
    task.cancel()


app = FastAPI(
    title="ネコスイ API",
    description="気分屋な猫と距離感を育てるゲームのバックエンド",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 本番では適切に制限すること
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- エンドポイント ---

@app.get("/api/saved-session")
async def get_saved_session():
    """保存済みセッションを返す。なければ404。"""
    session_id = _load_saved_session()
    if not session_id:
        raise HTTPException(status_code=404, detail="No saved session")
    status = await get_session_status(session_id)
    if status is None:
        _clear_saved_session()
        raise HTTPException(status_code=404, detail="Session expired")
    return {"session_id": session_id, "cat_name": status.cat.name}


@app.delete("/api/saved-session")
async def delete_saved_session():
    """保存済みセッションを削除する（新しい猫を作るとき）。"""
    _clear_saved_session()
    return {"status": "cleared"}


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "version": "0.1.0", "llm": is_llm_enabled(), "llm_provider": active_provider()}


@app.post("/api/cat/setup", response_model=SetupResponse)
async def setup_cat(req: CatSetupRequest):
    """新しい猫を作成し、セッションを開始する。"""
    init_data = create_new_cat(req.personality)
    cat_id, session_id = await create_cat_and_session(
        name=req.name,
        personality=req.personality,
        fur_color=req.fur_color,
        birthday=init_data.birthday,
        neuro_state=init_data.neuro_state,
    )
    _save_session(session_id)  # サーバー側に保存

    # 初日のあいさつ（O値で変化）
    o = init_data.neuro_state["O"]
    if req.personality == "tsundere":
        greeting = f"…({req.name}は興味なさそうにこちらを見た)" if o < 30 else f"…べつに、気になったわけじゃないから"
    elif req.personality == "amaenbo":
        greeting = f"にゃ〜ん！" if o >= 30 else f"…（じっとこちらを見ている）"
    else:
        greeting = "…（ゆっくりこちらに近づいてきた）"

    neuro_view = _neuro_dict_to_view(init_data.neuro_state)

    return SetupResponse(
        session_id=session_id,
        cat={"cat_id": cat_id, "name": req.name,
             "personality": req.personality, "fur_color": req.fur_color,
             "birthday": init_data.birthday},
        initial_state=neuro_view,
        greeting=greeting,
    )


@app.get("/api/cat/status/{session_id}", response_model=SessionStatus)
async def get_status(session_id: str):
    """セッションの現在状態を取得する。"""
    status = await get_session_status(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")
    return status


@app.post("/api/chat", response_model=CatResponse)
async def chat(req: ChatRequest):
    """ユーザーのアクションに対する猫の反応を返す。"""
    # セッション取得
    status = await get_session_status(req.session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")

    cat = status.cat
    neuro_dict = {
        "D": status.neuro_state.D,
        "S": status.neuro_state.S,
        "C": status.neuro_state.C,
        "O": status.neuro_state.O,
        "G": status.neuro_state.G,
        "E": status.neuro_state.E,
        "corruption": status.neuro_state.corruption,
    }
    is_fled = status.is_fled
    consecutive = status.consecutive_nekosui
    relationship = status.relationship_level
    time_info = get_time_period()
    event_log: list[str] = []

    # --- 逃げてる猫が戻るか判定（毎アクションで確認） ---
    if is_fled:
        # アクションによってS・Gを回復ブースト（性格差あり）
        neuro_dict = apply_action_recovery_boost(neuro_dict, req.action, cat.personality)
        event_log.append(f"recovery_boost: action={req.action} personality={cat.personality}")

        if decide_can_return(neuro_dict):
            is_fled = False
            consecutive = 0
            event_log.append("猫が戻ってきた")
            await add_chat_log(
                req.session_id, "cat", None,
                "（戻ってきた）", "sit", "normal",
            )

    # --- アクション実行 ---
    state_event, action_result = get_action_event(
        action=req.action,
        consecutive_nekosui=consecutive,
        neuro_state=neuro_dict,
        personality=cat.personality,
    )
    event_log.append(f"action={req.action} result={action_result}")

    # --- NeuroState 更新 ---
    delta = state_event.to_delta()
    new_neuro = apply_state_delta(neuro_dict, delta)
    event_log.append(f"O: {neuro_dict['O']:.1f} → {new_neuro['O']:.1f}")

    # --- 連続猫吸いカウント更新 ---
    if req.action == "nekosui":
        if action_result == "flee":
            new_consecutive = 0  # 逃げたらリセット
        else:
            new_consecutive = consecutive + 1
    else:
        new_consecutive = 0  # 他アクションでリセット

    # --- 逃げる判定 ---
    new_is_fled = is_fled
    if action_result in ("flee", "escape"):
        new_is_fled = True
        new_consecutive = 0
        event_log.append("猫が逃げた")

    # --- 行動決定 ---
    behavior: BehaviorDecision = decide_cat_behavior(
        action_result=action_result,
        action=req.action,
        neuro_state=new_neuro,
        personality=cat.personality,
        time_info=time_info,
        is_currently_fled=new_is_fled,
    )

    # --- 親密度更新 ---
    rel_gain = compute_relationship_gain(action_result, new_neuro["O"])
    new_relationship = max(0.0, min(1.0, relationship + rel_gain))
    event_log.append(f"relationship: {relationship:.3f} → {new_relationship:.3f}")

    # --- LLMでセリフ生成（APIキーがあれば） ---
    action_desc = _action_to_desc(req.action, req.text)
    system_prompt = build_cat_system_prompt(
        cat_name=cat.name,
        personality=cat.personality,
        time_info=time_info,
        neuro_state=new_neuro,
        relationship_level=new_relationship,
        is_fled=new_is_fled,
    )
    final_message = await generate_cat_response(
        system_prompt=system_prompt,
        user_action=action_desc,
        fallback_message=behavior.message,
    )
    event_log.append(f"llm={'on' if is_llm_enabled() else 'off(fallback)'}")

    # --- DB更新 ---
    await update_session(
        session_id=req.session_id,
        neuro_state=new_neuro,
        relationship_level=new_relationship,
        is_fled=new_is_fled,
        consecutive_nekosui=new_consecutive,
    )

    # --- ログ保存 ---
    user_text = req.text or req.action
    await add_chat_log(req.session_id, "user", req.action, user_text)
    await add_chat_log(
        req.session_id, "cat", None,
        final_message, behavior.pose, behavior.expression,
    )

    return CatResponse(
        message=final_message,
        pose=behavior.pose,
        expression=behavior.expression,
        sound=behavior.sound,
        is_fled=new_is_fled,
        neuro_state=_neuro_dict_to_view(new_neuro),
        relationship_level=new_relationship,
        event_log=event_log,
    )


@app.post("/api/cat/reset/{session_id}")
async def reset_cat(session_id: str):
    """セッションを今日の気分（ランダム）でリセットする。"""
    status = await get_session_status(session_id)
    if status is None:
        raise HTTPException(status_code=404, detail="セッションが見つかりません")

    from cat_initializer import generate_initial_neuro_state
    new_neuro = generate_initial_neuro_state(
        personality=status.cat.personality,
        cat_birthday=status.cat.birthday,
    )
    await reset_session(session_id, new_neuro)
    return {"status": "reset", "neuro_state": new_neuro}
