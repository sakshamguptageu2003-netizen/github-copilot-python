import sudoku_generator
import sudoku_solver
import sudoku_validation


def test_validation_module_provides_safe_check():
    board = sudoku_generator.create_empty_board()
    assert sudoku_validation.is_safe(board, 0, 0, 5) is True


def test_solver_module_can_fill_a_board():
    board = sudoku_generator.create_empty_board()
    assert sudoku_solver.fill_board(board) is True
    assert all(cell != sudoku_validation.EMPTY for row in board for cell in row)


def test_generator_module_produces_puzzle_and_solution():
    puzzle, solution = sudoku_generator.generate_puzzle(clues=35)
    assert len(puzzle) == 9
    assert len(solution) == 9
    assert sum(1 for row in puzzle for cell in row if cell != sudoku_validation.EMPTY) == 35
