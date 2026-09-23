from dataclasses import dataclass

@dataclass
class TurnManager:
    player_ids: list[str]
    current_index: int = 0

    @property
    def current_player_id(self) -> str | None:
        return self.player_ids[self.current_index] if self.player_ids else None

    def add_player(self, player_id: str) -> None:
        if player_id not in self.player_ids:
            self.player_ids.append(player_id)

    def remove_player(self, player_id: str) -> None:
        if player_id not in self.player_ids:
            return
        index = self.player_ids.index(player_id)
        self.player_ids.remove(player_id)
        if self.player_ids:
            self.current_index = index % len(self.player_ids)
        else:
            self.current_index = 0

    def advance(self) -> str | None:
        if not self.player_ids:
            return None
        self.current_index = (self.current_index + 1) % len(self.player_ids)
        return self.current_player_id
