import json
import random
from pathlib import Path
from backend.game.questions import Question

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "questions.json"

class QuestionService:
    def __init__(self, path: Path = DATA_PATH):
        self.questions = [Question(**q) for q in json.loads(path.read_text(encoding="utf-8"))["questions"]]

    def get_random(self, category=None, difficulty=None):
        candidates = [q for q in self.questions if (category is None or q.category == category) and (difficulty is None or q.difficulty == difficulty)]
        if not candidates:
            raise ValueError("No matching grammar questions found.")
        return random.choice(candidates)

question_service = QuestionService()
