from backend.services.question_service import question_service

def test_questions_load():
    question = question_service.get_random()
    assert question.options

def test_question_answer():
    question = question_service.get_random(category="verb_tenses", difficulty="A2")
    index = next(i for i, option in enumerate(question.options) if option["correct"])
    assert question.is_correct(index)
