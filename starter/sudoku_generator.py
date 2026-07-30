import copy
import random

from sudoku_solver import fill_board
from sudoku_validation import EMPTY, SIZE, is_safe


def deep_copy(board):
    return copy.deepcopy(board)


def create_empty_board():
    return [[EMPTY for _ in range(SIZE)] for _ in range(SIZE)]


def count_solutions(board):
    """Count the number of solutions for a Sudoku board using backtracking.

    The search stops once two solutions have been found, which keeps the
    implementation fast while still proving whether a puzzle is unique.
    """
    solutions = 0

    def search(state):
        nonlocal solutions
        if solutions >= 2:
            return

        for row in range(SIZE):
            for col in range(SIZE):
                if state[row][col] == EMPTY:
                    for value in range(1, SIZE + 1):
                        if is_safe(state, row, col, value):
                            state[row][col] = value
                            search(state)
                            state[row][col] = EMPTY
                            if solutions >= 2:
                                return
                    return

        solutions += 1

    search(deep_copy(board))
    return solutions


def remove_cells(board, clues):
    """Remove clues while keeping the puzzle uniquely solvable."""
    cells = [(row, col) for row in range(SIZE) for col in range(SIZE)]
    random.shuffle(cells)

    while sum(1 for row in board for cell in row if cell != EMPTY) > clues:
        removed_any = False
        for row, col in cells:
            if sum(1 for r in board for cell in r if cell != EMPTY) <= clues:
                break
            if board[row][col] == EMPTY:
                continue

            original_value = board[row][col]
            board[row][col] = EMPTY
            if count_solutions(board) != 1:
                board[row][col] = original_value
            else:
                removed_any = True

        if not removed_any:
            break


def generate_puzzle(clues=35):
    board = create_empty_board()
    fill_board(board)
    solution = deep_copy(board)
    remove_cells(board, clues)
    puzzle = deep_copy(board)
    return puzzle, solution
