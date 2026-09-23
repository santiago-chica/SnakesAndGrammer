from dataclasses import dataclass, field
import random

@dataclass
class Board:
    size: int = 100
    snake_count: int = 10
    ladder_count: int = 10
    snakes: dict[int, int] = field(default_factory=dict)
    ladders: dict[int, int] = field(default_factory=dict)
    special_squares: set[int] = field(default_factory=set)

    def generate(self, rng: random.Random | None = None) -> None:
        rng = rng or random.Random()
        self.snakes.clear()
        self.ladders.clear()
        occupied: set[int] = {1, self.size}

        def available_pairs(count: int, lower_start: bool):
            attempts = 0
            result = {}
            while len(result) < count and attempts < count * 500:
                attempts += 1
                a = rng.randint(2, self.size - 1)
                b = rng.randint(2, self.size - 1)
                if a == b or a in occupied or b in occupied:
                    continue
                start, end = (max(a, b), min(a, b)) if not lower_start else (min(a, b), max(a, b))
                result[start] = end
                occupied.update((start, end))
            return result

        self.snakes = available_pairs(self.snake_count, False)
        self.ladders = available_pairs(self.ladder_count, True)

    def generate_special_squares(self, rng: random.Random | None = None, count: int = 0) -> None:
        rng = rng or random.Random()
        self.special_squares.clear()
        if count <= 0:
            return
        candidates = list(range(2, self.size))
        rng.shuffle(candidates)
        self.special_squares = set(candidates[:count])

    def is_special_square(self, position: int) -> bool:
        return position in self.special_squares

    def destination(self, position: int) -> tuple[int, str | None]:
        if position in self.snakes:
            return self.snakes[position], "snake"
        if position in self.ladders:
            return self.ladders[position], "ladder"
        return position, None

    def move(self, current: int, roll: int, exact_finish: bool = True) -> int:
        destination = current + roll
        if exact_finish and destination > self.size:
            return current
        return min(destination, self.size)
