from dataclasses import dataclass

@dataclass(frozen=True)
class PowerUp:
    id: str
    name: str
    description: str

class PowerUpRegistry:
    def __init__(self, powers: list[PowerUp]):
        self._powers = {power.id: power for power in powers}

    def get(self, power_id: str) -> PowerUp | None:
        return self._powers.get(power_id)

    def all(self) -> list[PowerUp]:
        return list(self._powers.values())
