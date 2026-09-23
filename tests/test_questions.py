import asyncio
import random

from backend.game.game import Game
from backend.game.player import Player
from backend.models.game_models import GameSettings
from backend.services.question_service import question_service


def test_questions_load():
    question = question_service.get_random()
    assert question.options


def test_question_answer():
    question = question_service.get_random(category="verb_tenses", difficulty="A2")
    index = next(i for i, option in enumerate(question.options) if option["correct"])
    assert question.is_correct(index)


def test_game_queues_question_on_special_square():
    game = Game("TEST", Player.create("host"), GameSettings(question_categories=["verb_tenses"], question_difficulty="A2"))
    game.board.special_squares = {2}
    player = game.players[game.host_id]
    player.position = 2

    game.engine.queue_question_for_player(game.host_id)

    assert player.pending_question is not None
    assert player.pending_question["category"] == "verb_tenses"
    assert player.pending_question["difficulty"] == "A2"
    assert game.host_id in game.players and player.queued_questions


def test_board_keeps_special_squares_when_created():
    game = Game("TEST", Player.create("host"), GameSettings(special_square_count=3, min_players=1))
    game.engine.start()

    assert len(game.board.special_squares) == 3
    assert all(square in range(2, game.board.size) for square in game.board.special_squares)


def test_roll_can_trigger_question_on_random_chance():
    game = Game("TEST", Player.create("host"), GameSettings(min_players=1))
    game.state = "playing"
    game.turn = type("Turn", (), {"current_player_id": game.host_id})()
    player = game.players[game.host_id]
    player.position = 1
    game.engine.rng = random.Random(0)
    game.engine.rng.random = lambda: 0.1

    game.engine.roll(game.host_id)

    assert player.pending_question is not None


def test_answer_question_applies_ladder_after_correct_answer():
    async def run_test():
        game = Game("TEST", Player.create("host"), GameSettings(min_players=1))
        game.state = "playing"
        player = game.players[game.host_id]
        player.position = 12
        game.board.ladders = {15: 20}
        game.turn.current_index = 0
        player.pending_question = {
            "id": "present-simple-001",
            "question": "She ___ to school every day.",
            "options": [{"text": "go", "correct": False}, {"text": "goes", "correct": True}],
        }
        await game.handle_message(game.host_id, {"type": "answer_question", "option_index": 1})
        assert player.position == 20

    asyncio.run(run_test())


def test_host_can_restart_game():
    async def run_test():
        game = Game("TEST", Player.create("host"), GameSettings(min_players=1))
        game.state = "finished"
        game.winner_id = game.host_id
        host = game.players[game.host_id]
        host.position = 100
        host.pending_question = {"id": "x"}
        await game.handle_message(game.host_id, {"type": "restart_game"})
        assert game.state == "playing"
        assert game.winner_id is None
        assert host.position == 1
        assert host.pending_question is None
        assert game.turn.current_player_id == game.host_id

    asyncio.run(run_test())


def test_start_clears_stale_winner_state():
    game = Game("TEST", Player.create("host"), GameSettings(min_players=1))
    game.state = "finished"
    game.winner_id = game.host_id
    game.players[game.host_id].position = 100

    game.engine.start()

    assert game.state == "playing"
    assert game.winner_id is None
    assert game.players[game.host_id].position == 1
