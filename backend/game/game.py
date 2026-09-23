from collections import deque
from fastapi import WebSocket

from backend.game.board import Board
from backend.game.engine import GameEngine
from backend.game.events import event
from backend.game.player import Player
from backend.game.turn import TurnManager
from backend.models.game_models import GameSettings, GameSummary

class Game:
    def __init__(self, game_id: str, host_player: Player, settings: GameSettings | None = None):
        self.id = game_id
        self.state = "idle"
        self.host_id = host_player.id
        self.winner_id: str | None = None
        self.settings = settings or GameSettings()
        self.players: dict[str, Player] = {host_player.id: host_player}
        self.board = Board(self.settings.board_size, self.settings.snake_count, self.settings.ladder_count)
        self.turn = TurnManager([host_player.id])
        self.connections: dict[str, WebSocket] = {}
        self.chat: deque[dict] = deque(maxlen=100)
        self.engine = GameEngine(self)

    def add_player(self, username: str) -> Player:
        if self.state != "idle":
            raise ValueError("Game has already started.")
        if len(self.players) >= self.settings.max_players:
            raise ValueError("Game is full.")
        if any(p.username.casefold() == username.casefold() for p in self.players.values()):
            raise ValueError("Username is already taken.")
        player = Player.create(username)
        self.players[player.id] = player
        self.turn.add_player(player.id)
        return player

    def get_player(self, player_id: str) -> Player | None:
        return self.players.get(player_id)

    def connect_player(self, player_id: str, websocket: WebSocket) -> None:
        self.players[player_id].connected = True
        self.connections[player_id] = websocket

    def disconnect_player(self, player_id: str) -> None:
        if player_id in self.players:
            self.players[player_id].connected = False
        self.connections.pop(player_id, None)

    async def broadcast(self, payload: dict) -> None:
        dead = []
        for player_id, websocket in list(self.connections.items()):
            try:
                await websocket.send_json(payload)
            except Exception:
                dead.append(player_id)
        for player_id in dead:
            self.disconnect_player(player_id)

    async def handle_message(self, player_id: str, message: dict) -> None:
        message_type = message.get("type")
        try:
            if message_type == "start_game":
                if player_id != self.host_id:
                    raise ValueError("Only the host can start the game.")
                for item in self.engine.start():
                    await self.broadcast(item)
                await self.broadcast({"type": "game_state", "data": self.public_state()})

            elif message_type == "roll_dice":
                for item in self.engine.roll(player_id):
                    await self.broadcast(item)
                await self.broadcast({"type": "game_state", "data": self.public_state()})

            elif message_type == "chat":
                text = str(message.get("message", "")).strip()
                if text:
                    text = text[: self.settings.max_chat_message_length]
                    item = {"player_id": player_id, "username": self.players[player_id].username, "message": text}
                    self.chat.append(item)
                    await self.broadcast(event("chat_message", **item))

            elif message_type == "emote":
                await self.broadcast(event("emote_played", player_id=player_id, emote=str(message.get("emote", ""))))

            else:
                raise ValueError(f"Unknown message type: {message_type}")
        except ValueError as exc:
            websocket = self.connections.get(player_id)
            if websocket:
                await websocket.send_json(event("error", message=str(exc)))

    def public_state(self) -> dict:
        return {
            "id": self.id,
            "state": self.state,
            "host_id": self.host_id,
            "winner_id": self.winner_id,
            "settings": self.settings.model_dump(),
            "board": {"size": self.board.size, "snakes": self.board.snakes, "ladders": self.board.ladders},
            "players": [
                {"id": p.id, "username": p.username, "position": p.position, "powerups": p.powerups,
                 "queued_questions": len(p.queued_questions), "connected": p.connected}
                for p in self.players.values()
            ],
            "current_player_id": self.turn.current_player_id,
            "chat": list(self.chat),
        }

    def summary(self) -> GameSummary:
        return GameSummary(
            id=self.id,
            state=self.state,
            host_id=self.host_id,
            players=[{"id": p.id, "username": p.username, "position": p.position} for p in self.players.values()],
        )
