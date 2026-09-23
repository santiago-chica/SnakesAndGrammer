import random

from backend.game.events import event
from backend.services.question_service import question_service


class GameEngine:
    def __init__(self, game):
        self.game = game
        self.rng = random.Random()

    def start(self) -> list[dict]:
        if self.game.state not in {"idle", "finished"}:
            raise ValueError("Game has already started.")
        if len(self.game.players) < self.game.settings.min_players:
            raise ValueError("Not enough players to start.")

        self.game.winner_id = None
        for player in self.game.players.values():
            player.position = 1
            player.pending_question = None
            player.queued_questions.clear()

        self.game.board.generate(self.rng)
        self.game.board.generate_special_squares(self.rng, self.game.settings.special_square_count)
        self.game.state = "playing"
        return [event("game_started")]

    def queue_question_for_player(self, player_id: str) -> dict:
        player = self.game.players[player_id]
        if player.pending_question is not None:
            return event("question_queued", player_id=player_id, question=player.pending_question)

        categories = self.game.settings.question_categories or None
        difficulty = self.game.settings.question_difficulty
        question = question_service.get_random(category=categories, difficulty=difficulty)
        payload = {
            "id": question.id,
            "category": question.category,
            "difficulty": question.difficulty,
            "question": question.question,
            "options": question.options,
        }
        player.pending_question = payload
        player.queued_questions = [question.id]
        return event("question_queued", player_id=player_id, question=payload)

    def roll(self, player_id: str) -> list[dict]:
        if self.game.state != "playing":
            raise ValueError("Game is not playing.")
        if self.game.turn.current_player_id != player_id:
            raise ValueError("It is not your turn.")

        player = self.game.players[player_id]
        if player.pending_question is not None or player.queued_questions:
            raise ValueError("You must answer your queued question first.")

        roll = self.rng.randint(1, self.game.settings.dice_sides)
        events = [event("dice_rolled", player_id=player_id, value=roll)]
        old_position = player.position
        new_position = self.game.board.move(old_position, roll, self.game.settings.exact_finish)
        question_queued = False

        if new_position == old_position and old_position + roll > self.game.board.size:
            events.append(event("move_blocked", player_id=player_id, position=old_position))
        else:
            player.position = new_position
            events.append(event("player_moved", player_id=player_id, from_position=old_position, to_position=new_position))

            destination, kind = self.game.board.destination(player.position)
            if kind:
                player.position = destination
                events.append(event(f"{kind}_triggered", player_id=player_id, from_position=new_position, to_position=destination))

            if self.game.board.is_special_square(player.position) or self.rng.random() < 0.30:
                question_event = self.queue_question_for_player(player_id)
                events.append(question_event)
                question_queued = True

        if player.position == self.game.board.size:
            self.game.state = "finished"
            self.game.winner_id = player_id
            events.append(event("game_won", player_id=player_id))
            return events

        if question_queued:
            return events

        if not (self.game.settings.extra_turn_on_six and roll == 6):
            self.game.turn.advance()

        events.append(event("turn_changed", player_id=self.game.turn.current_player_id))
        return events
