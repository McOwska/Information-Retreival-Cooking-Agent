from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any, Dict, List


DATA_DIR = Path("data")
PREFERENCES_FILE = DATA_DIR / "user_preferences.json"
FAVORITES_FILE = DATA_DIR / "favorite_recipes.json"


def _ensure_data_files() -> None:
    """
    Creates the data directory and default JSON files if they do not exist yet.
    """
    DATA_DIR.mkdir(exist_ok=True)

    if not PREFERENCES_FILE.exists():
        PREFERENCES_FILE.write_text(
            json.dumps(
                {
                    "diet": None,
                    "liked_cuisines": [],
                    "disliked_ingredients": [],
                    "preferred_difficulty": None,
                    "preferred_cooking_time": None,
                    "notes": []
                },
                indent=2,
                ensure_ascii=False,
            ),
            encoding="utf-8",
        )

    if not FAVORITES_FILE.exists():
        FAVORITES_FILE.write_text(
            json.dumps([], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )


def _read_json(path: Path) -> Any:
    _ensure_data_files()
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, data: Any) -> None:
    _ensure_data_files()
    path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_user_preferences() -> Dict[str, Any]:
    """
    Returns the stored user preferences.
    """
    return _read_json(PREFERENCES_FILE)


def update_user_preferences(new_preferences: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates user preferences.

    For list fields, new values are appended without duplicates.
    For scalar fields, the value is overwritten.
    """
    preferences = get_user_preferences()

    for key, value in new_preferences.items():
        if key not in preferences:
            preferences[key] = value
            continue

        if isinstance(preferences[key], list):
            if isinstance(value, list):
                for item in value:
                    if item not in preferences[key]:
                        preferences[key].append(item)
            else:
                if value not in preferences[key]:
                    preferences[key].append(value)
        else:
            preferences[key] = value

    _write_json(PREFERENCES_FILE, preferences)
    return preferences


def get_favorite_recipes() -> List[Dict[str, Any]]:
    """
    Returns all saved favorite recipes.
    """
    return _read_json(FAVORITES_FILE)


def save_favorite_recipe(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """
    Saves a recipe to favorites.

    Expected recipe fields:
    - name
    - ingredients
    - instructions
    - tags
    - notes

    The function is flexible, so the model can pass partial recipe data too.
    """
    favorites = get_favorite_recipes()

    saved_recipe = {
        "id": f"fav_{uuid.uuid4().hex[:8]}",
        "name": recipe.get("name", "Unnamed recipe"),
        "ingredients": recipe.get("ingredients", []),
        "instructions": recipe.get("instructions", []),
        "tags": recipe.get("tags", []),
        "notes": recipe.get("notes", ""),
    }

    favorites.append(saved_recipe)
    _write_json(FAVORITES_FILE, favorites)

    return saved_recipe


def search_favorite_recipes(query: str) -> List[Dict[str, Any]]:
    """
    Simple keyword search over favorite recipes.
    Searches in name, ingredients, tags, and notes.
    """
    query_lower = query.lower().strip()
    favorites = get_favorite_recipes()

    if not query_lower:
        return favorites

    results = []

    for recipe in favorites:
        searchable_text = " ".join(
            [
                str(recipe.get("name", "")),
                " ".join(recipe.get("ingredients", [])),
                " ".join(recipe.get("tags", [])),
                str(recipe.get("notes", "")),
            ]
        ).lower()

        if query_lower in searchable_text:
            results.append(recipe)

    return results


def remove_favorite_recipe(recipe_id: str) -> bool:
    """
    Removes a favorite recipe by id.
    Returns True if something was removed, otherwise False.
    """
    favorites = get_favorite_recipes()
    updated_favorites = [
        recipe for recipe in favorites if recipe.get("id") != recipe_id
    ]

    if len(updated_favorites) == len(favorites):
        return False

    _write_json(FAVORITES_FILE, updated_favorites)
    return True