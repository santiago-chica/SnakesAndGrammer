from dataclasses import dataclass

@dataclass(frozen=True)
class GameDefaults:
    board_size: int = 100
    min_players: int = 1
    max_players: int = 8
    dice_sides: int = 6
    chat_history_limit: int = 100
    max_chat_message_length: int = 250
    exact_finish: bool = True
    extra_turn_on_six: bool = False
    snake_count: int = 10
    ladder_count: int = 10
    special_square_count: int = 15
    powerup_count: int = 8
    max_powerups: int = 2
    turn_time_limit_seconds: int | None = None

DEFAULTS = GameDefaults()
