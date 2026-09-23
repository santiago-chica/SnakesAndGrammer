from pydantic import BaseModel, Field, field_validator

class GameSettings(BaseModel):
    board_size: int = Field(100, ge=20, le=500)
    min_players: int = Field(1, ge=1, le=16)
    max_players: int = Field(8, ge=1, le=16)
    dice_sides: int = Field(6, ge=2, le=20)
    exact_finish: bool = True
    extra_turn_on_six: bool = False
    snake_count: int = Field(10, ge=0, le=100)
    ladder_count: int = Field(10, ge=0, le=100)
    special_square_count: int = Field(15, ge=0, le=100)
    powerup_count: int = Field(8, ge=0, le=100)
    max_powerups: int = Field(2, ge=1, le=2)
    turn_time_limit_seconds: int | None = Field(None, ge=5, le=600)
    question_difficulty: str | None = None
    question_categories: list[str] = Field(default_factory=list)
    powers_enabled: bool = True

    @field_validator("max_players")
    @classmethod
    def max_players_positive(cls, value: int) -> int:
        return value

class CreateGameRequest(BaseModel):
    username: str = Field(min_length=1, max_length=24)
    settings: GameSettings = Field(default_factory=GameSettings)

class JoinGameRequest(BaseModel):
    username: str = Field(min_length=1, max_length=24)

class PlayerSummary(BaseModel):
    id: str
    username: str
    position: int

class GameSummary(BaseModel):
    id: str
    state: str
    host_id: str
    players: list[PlayerSummary]
