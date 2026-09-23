from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.services.game_manager import game_manager

router = APIRouter()

@router.websocket("/ws/games/{game_id}/{player_id}")
async def game_websocket(websocket: WebSocket, game_id: str, player_id: str):
    game = game_manager.get_game(game_id)
    if game is None or game.get_player(player_id) is None:
        await websocket.close(code=4004, reason="Game or player not found")
        return

    await websocket.accept()
    game.connect_player(player_id, websocket)
    await websocket.send_json({"type": "game_state", "data": game.public_state()})
    await game.broadcast({"type": "player_connected", "data": {"player_id": player_id}})

    try:
        while True:
            message = await websocket.receive_json()
            await game.handle_message(player_id, message)
    except WebSocketDisconnect:
        game.disconnect_player(player_id)
        await game.broadcast({"type": "player_disconnected", "data": {"player_id": player_id}})
