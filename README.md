# 🐍 Snakes & Ladders: Grammar Edition

Chaotic multiplayer grammar game: FastAPI + WebSockets + vanilla HTML/CSS/JS.

## Run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload
```

Then serve `frontend/` with a tiny static server (recommended):

```powershell
python -m http.server 5500 --directory frontend
```

Open `http://localhost:5500`.

## Current foundation

- In-memory game manager
- Host/join flow with short game IDs
- Server-authoritative WebSocket gameplay
- Random snakes and ladders
- Exact-finish rule
- Configurable board/game settings model
- Per-game chat capped at 100 messages
- Grammar question JSON supporting category + CEFR-like difficulty
- Emote JSON schema
- Power-up JSON schema
- Modular backend

## Next gameplay layers

1. Special-square generation and resolution.
2. Question squares with forward/backward movement.
3. Queued questions that must be answered on the affected player's turn.
4. Power-up inventory and the two-item maximum.
5. Slow/forced-question powers and more chaotic effects.
6. Host settings UI.
7. Better board rendering and animations.
8. Emote UI and audio.
9. Turn timers and reconnect handling.
10. Tests for every game rule.
