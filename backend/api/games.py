from fastapi import APIRouter, HTTPException

from backend.models.game_models import CreateGameRequest, JoinGameRequest, GameSummary
from backend.services.game_manager import game_manager

router = APIRouter()

@router.post("", response_model=GameSummary)
def create_game(request: CreateGameRequest):
    return game_manager.create_game(request).summary()

@router.post("/{game_id}/join", response_model=GameSummary)
async def join_game(game_id: str, request: JoinGameRequest):
    game = game_manager.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    try:
        player = game.add_player(request.username)
    except ValueError as exc:
        raise HTTPException(400, str(exc)) from exc

    for websocket in game.connections.values():
        await websocket.send_json({"type": "game_state", "data": game.public_state()})

    return GameSummary(
        id=game.id,
        state=game.state,
        host_id=game.host_id,
        players=[{"id": p.id, "username": p.username, "position": p.position} for p in game.players.values()],
    )

@router.get("/{game_id}", response_model=GameSummary)
def get_game(game_id: str):
    game = game_manager.get_game(game_id)
    if game is None:
        raise HTTPException(404, "Game not found")
    return game.summary()
