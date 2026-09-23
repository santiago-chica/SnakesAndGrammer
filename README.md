# 🐍 Snakes & Ladders: Grammar Edition

Chaotic multiplayer grammar game: FastAPI + WebSockets + vanilla HTML/CSS/JS.

## Super simple run

From the repo root, run one of these:

```powershell
./start-backend.ps1
```

```powershell
./start-frontend.ps1
```

```powershell
./start-all.ps1
```

Then open:

- Local app: http://localhost:5500
- Local API docs: http://localhost:8000/docs

## ngrok quick tunnel

```powershell
./start-ngrok.ps1
```

Then open the frontend with the backend tunnel in the URL, for example:

```text
http://localhost:5500/?api=https://<your-backend-ngrok-url>
```

If you want the frontend itself tunneled too, run:

```powershell
ngrok http 5500
```

## Manual run

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
```

Then serve the frontend:

```powershell
python -m http.server 5500 --directory frontend
```

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
