# CookMate (Python)

CookMate is a small cooking assistant agent with lightweight local memory (preferences + favorite recipes). It’s a Python re-implementation of the TypeScript agent template in [BirgerMoell/agents](https://github.com/BirgerMoell/agents), adapted to use Berget’s OpenAI-compatible Chat Completions API with tool calling.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `BERGET_API_KEY` (or `OPENAI_API_KEY`) in `.env`, then:

```bash
python3 agent.py
```

## What it does

- Suggests recipes based on your constraints (diet, allergies, time, equipment, ingredients).
- Stores stable preferences in `data/user_preferences.json`.
- Lets you save/search/remove favorite recipes in `data/favorite_recipes.json`.

## Memory

CookMate persists to local JSON files under `data/`:

- `data/user_preferences.json` (diet, allergies, cuisines, dislikes, time, difficulty, notes)
- `data/favorite_recipes.json` (saved recipes with `id`, `ingredients`, `instructions`, `tags`, `notes`)

If you want a “fresh” agent, delete those files.

## Example prompts

- “I have eggs, spinach, and feta. Dinner in 25 minutes.”
- “I’m lactose intolerant and vegetarian. Suggest 3 weeknight meals under 45 minutes.”
- “Save this recipe.”
- “Show my favorite recipes.”
- “Find favorites with ‘pasta’.”
- “Remove favorite `fav_1234abcd`.”

## Configuration

Environment variables (see `.env.example`):

- `BERGET_API_KEY` (recommended) or `OPENAI_API_KEY`
- `BASE_URL` (default: `https://api.berget.ai/v1`)
- `MODEL` (default: `openai/gpt-oss-120b`)
- `TEMPERATURE` (default: `0.7`)
- `MAX_TOKENS` (default: `512`)
- `SKILLS_DIR` (default: `.skills`)

## Skills (optional)

The agent supports a local `.skills/` directory containing Agent Skills-style folders:

```
.skills/
  example-skill/
    SKILL.md
    references/
      ...
    scripts/
      ...
```

At startup it injects an `<available_skills>` block into the system prompt, and exposes:

- `list_skills`
- `load_skill`
- `read_skill_file`
