import secrets
import string

from backend.game.game import Game
from backend.game.player import Player
from backend.models.game_models import CreateGameRequest

class GameManager:
    def __init__(self):
        self.games: dict[str, Game] = {}

    def _new_id(self) -> str:
        alphabet = string.ascii_uppercase + string.digits
        while True:
            game_id = "".join(secrets.choice(alphabet) for _ in range(6))
            if game_id not in self.games:
                return game_id

    def create_game(self, request: CreateGameRequest) -> Game:
        game_id = self._new_id()
        game = Game(game_id, Player.create(request.username), request.settings)
        self.games[game_id] = game
        return game

    def get_game(self, game_id: str) -> Game | None:
        return self.games.get(game_id.upper())

    def delete_game(self, game_id: str) -> None:
        self.games.pop(game_id.upper(), None)

game_manager = GameManager()
