from dataclasses import dataclass, field
import secrets

@dataclass
class Player:
    id: str
    username: str
    position: int = 1
    powerups: list[str] = field(default_factory=list)
    queued_questions: list[str] = field(default_factory=list)
    pending_question: dict | None = field(default=None, repr=False)
    connected: bool = False
    turn_effects: dict[str, int] = field(default_factory=dict)

    @classmethod
    def create(cls, username: str) -> "Player":
        return cls(id=secrets.token_urlsafe(9), username=username)

    def add_powerup(self, powerup_id: str, max_powerups: int = 2) -> bool:
        if len(self.powerups) >= max_powerups:
            return False
        self.powerups.append(powerup_id)
        return True

    def remove_powerup(self, powerup_id: str) -> bool:
        if powerup_id not in self.powerups:
            return False
        self.powerups.remove(powerup_id)
        return True
