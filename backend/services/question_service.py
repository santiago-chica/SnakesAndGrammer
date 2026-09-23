import json
import random
from pathlib import Path
from backend.game.questions import Question

DATA_PATH = Path(__file__).resolve().parent.parent / "data" / "questions.json"


class QuestionService:
    def __init__(self, path: Path = DATA_PATH):
        self.questions = [Question(**q) for q in json.loads(path.read_text(encoding="utf-8"))["questions"]]
        self.by_id = {question.id: question for question in self.questions}

    def get_by_id(self, question_id: str) -> Question | None:
        return self.by_id.get(question_id)

    def get_random(self, category=None, difficulty=None):
        categories = set(category) if isinstance(category, (list, tuple, set)) else None
        candidates = [
            q for q in self.questions
            if (categories is None or q.category in categories)
            and (difficulty is None or q.difficulty == difficulty)
        ]
        if not candidates:
            raise ValueError("No matching grammar questions found.")
        return random.choice(candidates)


question_service = QuestionService()
