from backend.game.board import Board

def test_board_generates_pairs():
    board = Board()
    board.generate()
    assert len(board.snakes) == 10
    assert len(board.ladders) == 10
    assert all(start > end for start, end in board.snakes.items())
    assert all(start < end for start, end in board.ladders.items())

def test_exact_finish_blocks_overshoot():
    board = Board()
    assert board.move(98, 6, True) == 98
