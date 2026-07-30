import random

from sudoku_validation import EMPTY, SIZE, is_safe


def fill_board(board):
    """Fill an empty Sudoku board using backtracking."""
    for row in range(SIZE):
        for col in range(SIZE):
            if board[row][col] == EMPTY:
                possible = list(range(1, SIZE + 1))
                random.shuffle(possible)
                for candidate in possible:
                    if is_safe(board, row, col, candidate):
                        board[row][col] = candidate
                        if fill_board(board):
                            return True
                        board[row][col] = EMPTY
                return False
    return True


def solve_board(board):
    """Convenience wrapper for solving a board in place."""
    return fill_board(board)
