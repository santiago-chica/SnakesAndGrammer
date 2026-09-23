from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Question:
    id: str
    category: str
    difficulty: str
    question: str
    options: list[dict[str, Any]]

    def is_correct(self, option_index: int) -> bool:
        return 0 <= option_index < len(self.options) and bool(self.options[option_index]["correct"])
