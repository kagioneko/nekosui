"""LLMクライアント

対応プロバイダー:
  - anthropic   : Claude Haiku（デフォルト）
  - openai      : GPT-4o-mini
  - gemini      : Gemini 2.0 Flash
  - openrouter  : OpenRouter（モデルは OPENROUTER_MODEL で指定）

優先順位（LLM_PROVIDER 未設定時）:
  ANTHROPIC_API_KEY → OPENAI_API_KEY → GEMINI_API_KEY → OPENROUTER_API_KEY

どのキーも未設定の場合はテンプレートセリフで動作します。
"""

from __future__ import annotations
import os
import logging

logger = logging.getLogger(__name__)

# --- プロバイダー検出 ---

_PROVIDER = os.getenv("LLM_PROVIDER", "").strip().lower()

_ANTHROPIC_KEY  = os.getenv("ANTHROPIC_API_KEY", "").strip()
_OPENAI_KEY     = os.getenv("OPENAI_API_KEY", "").strip()
_GEMINI_KEY     = os.getenv("GEMINI_API_KEY", "").strip()
_OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "").strip()
_OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini").strip()

# LLM_PROVIDER 未指定なら持っているキーを順番に試す
if not _PROVIDER:
    if _ANTHROPIC_KEY:
        _PROVIDER = "anthropic"
    elif _OPENAI_KEY:
        _PROVIDER = "openai"
    elif _GEMINI_KEY:
        _PROVIDER = "gemini"
    elif _OPENROUTER_KEY:
        _PROVIDER = "openrouter"

_LLM_ENABLED = bool(_PROVIDER)

if _LLM_ENABLED:
    logger.info("[llm] プロバイダー: %s", _PROVIDER)
else:
    logger.info("[llm] APIキー未設定 → テンプレートフォールバックモード")


# --- 各プロバイダーの生成関数 ---

async def _call_anthropic(system_prompt: str, user_action: str) -> str:
    import anthropic
    client = anthropic.AsyncAnthropic(api_key=_ANTHROPIC_KEY)
    message = await client.messages.create(
        model="claude-haiku-4-5-20251001",
        max_tokens=80,
        system=system_prompt,
        messages=[{"role": "user", "content": user_action}],
    )
    return message.content[0].text.strip()


async def _call_openai(system_prompt: str, user_action: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(api_key=_OPENAI_KEY)
    resp = await client.chat.completions.create(
        model="gpt-4o-mini",
        max_tokens=80,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_action},
        ],
    )
    return resp.choices[0].message.content.strip()


async def _call_gemini(system_prompt: str, user_action: str) -> str:
    import google.generativeai as genai
    genai.configure(api_key=_GEMINI_KEY)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_prompt,
    )
    resp = await model.generate_content_async(user_action)
    return resp.text.strip()


async def _call_openrouter(system_prompt: str, user_action: str) -> str:
    from openai import AsyncOpenAI
    client = AsyncOpenAI(
        api_key=_OPENROUTER_KEY,
        base_url="https://openrouter.ai/api/v1",
    )
    resp = await client.chat.completions.create(
        model=_OPENROUTER_MODEL,
        max_tokens=80,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user",   "content": user_action},
        ],
    )
    return resp.choices[0].message.content.strip()


_CALLERS = {
    "anthropic":  _call_anthropic,
    "openai":     _call_openai,
    "gemini":     _call_gemini,
    "openrouter": _call_openrouter,
}


# --- 公開 API ---

async def generate_cat_response(
    system_prompt: str,
    user_action: str,
    fallback_message: str,
) -> str:
    """猫のセリフを生成する。

    Args:
        system_prompt:    猫のシステムプロンプト（cat_prompt_builder製）
        user_action:      ユーザーのアクション説明（例: "猫吸いしてきた"）
        fallback_message: APIキーなし時のフォールバックセリフ

    Returns:
        猫のセリフ
    """
    if not _LLM_ENABLED:
        return fallback_message

    caller = _CALLERS.get(_PROVIDER)
    if caller is None:
        logger.warning("[llm] 未知のプロバイダー: %s → フォールバック", _PROVIDER)
        return fallback_message

    try:
        text = await caller(system_prompt, user_action)
        logger.debug("[llm] generated (%s): %s", _PROVIDER, text)
        return text
    except Exception as e:
        logger.warning("[llm] 生成失敗 (%s)、フォールバックを使用: %s", _PROVIDER, e)
        return fallback_message


def is_llm_enabled() -> bool:
    """LLMが有効かどうかを返す（ヘルスチェック用）。"""
    return _LLM_ENABLED


def active_provider() -> str:
    """現在使用中のプロバイダー名を返す。"""
    return _PROVIDER if _LLM_ENABLED else "none"
