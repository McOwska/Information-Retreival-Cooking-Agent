# CookMate

CookMate is a small cooking assistant agent with lightweight local memory (preferences + favorite recipes). It’s a Python re-implementation of the TypeScript agent template in [BirgerMoell/agents](https://github.com/BirgerMoell/agents), with few additional features to help you with finding cooking inspirations.

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
```

Set `BERGET_API_KEY` (or `OPENAI_API_KEY`) in `.env` (current KEY is just an invalid example!), then:

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

## Demo

A full recorded demo is available here: [DEMO_rec.mp4](./DEMO_rec.mp4).

Since the responses can take some time and the video is over 3 minutes long, a screenshot is included below as a quick preview of the interaction, to save your time :).

<img width="1505" height="937" alt="CookMate demo screenshot" src="https://github.com/user-attachments/assets/37ed0f20-acf7-4584-bbd8-69a6f84f828c" />



