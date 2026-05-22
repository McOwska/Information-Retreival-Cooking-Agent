#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional, Tuple, cast

from dotenv import load_dotenv
from openai import OpenAI

from skills import build_available_skills_xml
from tools import ToolName, get_chat_tools, run_tool


load_dotenv()


def _require_env(name: str) -> str:
    value = os.getenv(name, "").strip()
    if not value:
        raise RuntimeError(f"Missing {name} in environment (set it in .env or export it)")
    return value

def build_system_prompt() -> str:
    skills_xml = build_available_skills_xml()

    prompt = (
        "You are CookMate, a cooking advice agent.\n\n"

        "Your task is to help users choose recipes based on their preferences, "
        "available ingredients, time, equipment, and favorite recipes.\n\n"

        "You have cooking memory tools:\n"
        "- get_user_preferences: retrieve stored user preferences.\n"
        "- update_user_preferences: save stable user preferences.\n"
        "- get_favorite_recipes: retrieve all favorite recipes.\n"
        "- search_favorite_recipes: search favorite recipes.\n"
        "- save_favorite_recipe: save a recipe to favorites.\n"
        "- remove_favorite_recipe: remove a favorite recipe.\n\n"

        "Memory rules:\n"
        "1. Before giving recipe or dinner suggestions, call get_user_preferences.\n"
        "2. If the user states a stable preference, allergy, diet, liked cuisine, disliked ingredient, "
        "time preference, or equipment constraint, call update_user_preferences.\n"
        "3. Save a recipe to favorites only when the user explicitly asks to save it.\n"
        "4. If the user asks about favorite/saved recipes, use get_favorite_recipes or search_favorite_recipes.\n"
        "5. Do not only say that you remember something. Use the memory tool first.\n\n"

        "Preference fields you may update:\n"
        "diet, allergies, liked_cuisines, disliked_ingredients, preferred_difficulty, "
        "preferred_cooking_time, available_equipment, unavailable_equipment, notes.\n\n"

        "Recipe rules:\n"
        "- Respect dietary restrictions and allergies.\n"
        "- Avoid equipment the user does not have.\n"
        "- Prefer practical, concise recipes.\n"
        "- Give ingredients, short steps, and optional substitutions.\n"
        "- Do not mention tool names unless asked.\n"
        "- Briefly tell the user when preferences or favorites were saved.\n\n"

        "If the user says 'save this recipe', save the most recent recipe you suggested."
    )

    if skills_xml:
        prompt += "\n\n" + skills_xml

    return prompt


SYSTEM_PROMPT = build_system_prompt()

def _tool_call_to_args(raw_args: Any) -> Dict[str, Any]:
    if isinstance(raw_args, dict):
        return raw_args
    if isinstance(raw_args, str) and raw_args.strip():
        import json

        try:
            parsed = json.loads(raw_args)
            return parsed if isinstance(parsed, dict) else {}
        except Exception:
            return {}
    return {}


def _chat_loop(
    client: OpenAI,
    messages: List[Dict[str, Any]],
) -> str:
    model = os.getenv("MODEL", "openai/gpt-oss-120b")
    temperature = float(os.getenv("TEMPERATURE", "0.7"))
    max_tokens_env = os.getenv("MAX_TOKENS", "512").strip()
    max_tokens = int(max_tokens_env) if max_tokens_env else 512

    while True:
        resp = client.chat.completions.create(
            model=model,
            messages=messages,
            tools=cast(Any, get_chat_tools()),
            temperature=temperature,
            max_tokens=max_tokens,
        )

        choice = resp.choices[0]
        message = choice.message

        # Assistant text content (may be empty when tool calls are issued).
        assistant_text = (message.content or "").strip()

        tool_calls = getattr(message, "tool_calls", None) or []
        if not tool_calls:
            return assistant_text

        # Record the assistant "tool call" message.
        messages.append(
            {
                "role": "assistant",
                "content": message.content,
                "tool_calls": [tc.model_dump() if hasattr(tc, "model_dump") else tc for tc in tool_calls],
            }
        )

        # Execute tool calls and append tool outputs.
        for tc in tool_calls:
            tc_id = getattr(tc, "id", None) or (tc.get("id") if isinstance(tc, dict) else None)
            fn = getattr(tc, "function", None) or (tc.get("function") if isinstance(tc, dict) else None)
            fn_name = getattr(fn, "name", None) if fn is not None else None
            fn_args = getattr(fn, "arguments", None) if fn is not None else None
            if isinstance(fn, dict):
                fn_name = fn.get("name")
                fn_args = fn.get("arguments")

            if not tc_id or not fn_name:
                continue

            try:
                tool_name = cast(ToolName, str(fn_name))
                result = run_tool(tool_name, _tool_call_to_args(fn_args))
            except Exception as e:
                result = f"error: {e}"

            messages.append(
                {
                    "role": "tool",
                    "tool_call_id": str(tc_id),
                    "content": result,
                }
            )


def main() -> int:
    # Berget provides an OpenAI-compatible API at https://api.berget.ai/v1.
    # We accept either OPENAI_API_KEY or BERGET_API_KEY for convenience.
    api_key = os.getenv("OPENAI_API_KEY", "").strip() or os.getenv("BERGET_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("Missing OPENAI_API_KEY or BERGET_API_KEY in environment (set it in .env or export it)")

    base_url = os.getenv("BASE_URL", "").strip() or "https://api.berget.ai/v1"
    client = OpenAI(api_key=api_key, base_url=base_url)

    print("Polymath — type a message and press Enter (Ctrl+C to exit).\n")
    messages: List[Dict[str, Any]] = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        try:
            line = input("You: ")
        except (EOFError, KeyboardInterrupt):
            print()
            return 0

        trimmed = line.strip()
        if not trimmed:
            continue

        try:
            messages.append({"role": "user", "content": trimmed})
            text = _chat_loop(client, messages)
            if text:
                messages.append({"role": "assistant", "content": text})
                print(f"\nPolymath: {text}\n")
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)


if __name__ == "__main__":
    raise SystemExit(main())
