import pytest
import sudoku_logic


class TestBoardCreation:
    """Tests for board creation and initialization."""
    
    def test_create_empty_board(self):
        """Test that create_empty_board returns a 9x9 board filled with zeros."""
        board = sudoku_logic.create_empty_board()
        
        assert len(board) == 9
        assert all(len(row) == 9 for row in board)
        assert all(cell == sudoku_logic.EMPTY for row in board for cell in row)
    
    def test_deep_copy_creates_independent_copy(self):
        """Test that deep_copy creates an independent copy, not a reference."""
        original = sudoku_logic.create_empty_board()
        original[0][0] = 5
        
        copied = sudoku_logic.deep_copy(original)
        copied[0][0] = 9
        
        assert original[0][0] == 5
        assert copied[0][0] == 9


class TestBoardValidation:
    """Tests for Sudoku board validation rules."""
    
    def test_is_safe_empty_board(self):
        """Test that any number 1-9 is safe on an empty board."""
        board = sudoku_logic.create_empty_board()
        
        for num in range(1, 10):
            assert sudoku_logic.is_safe(board, 0, 0, num) is True
    
    def test_is_safe_row_conflict(self):
        """Test that is_safe detects conflicts in the same row."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        
        assert sudoku_logic.is_safe(board, 0, 5, 5) is False
        assert sudoku_logic.is_safe(board, 0, 5, 6) is True
    
    def test_is_safe_column_conflict(self):
        """Test that is_safe detects conflicts in the same column."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        
        assert sudoku_logic.is_safe(board, 5, 0, 5) is False
        assert sudoku_logic.is_safe(board, 5, 0, 6) is True
    
    def test_is_safe_box_conflict(self):
        """Test that is_safe detects conflicts in the same 3x3 box."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5
        
        # (1, 1) is in the same 3x3 box as (0, 0)
        assert sudoku_logic.is_safe(board, 1, 1, 5) is False
        # (1, 1) can have other numbers
        assert sudoku_logic.is_safe(board, 1, 1, 6) is True
    
    def test_is_safe_different_boxes(self):
        """Test that numbers can be placed in different 3x3 boxes."""
        board = sudoku_logic.create_empty_board()
        board[0][0] = 5  # Top-left 3x3 box
        
        # (3, 3) is in the center 3x3 box
        assert sudoku_logic.is_safe(board, 3, 3, 5) is True


class TestPuzzleGeneration:
    """Tests for puzzle generation."""
    
    def test_generate_puzzle_returns_two_boards(self):
        """Test that generate_puzzle returns puzzle and solution."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        
        assert isinstance(puzzle, list)
        assert isinstance(solution, list)
    
    def test_puzzle_is_9x9(self):
        """Test that generated puzzle is a valid 9x9 board."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        
        assert len(puzzle) == 9
        assert all(len(row) == 9 for row in puzzle)
    
    def test_solution_is_complete(self):
        """Test that solution has no empty cells."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        
        empty_count = sum(1 for row in solution for cell in row if cell == sudoku_logic.EMPTY)
        assert empty_count == 0
    
    def test_solution_has_valid_values(self):
        """Test that solution contains only valid Sudoku numbers (1-9)."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        
        for row in solution:
            for cell in row:
                assert 1 <= cell <= 9
    
    def test_puzzle_has_clues(self):
        """Test that generated puzzle has the requested number of clues."""
        clues = 35
        puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
        
        clue_count = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
        assert clue_count == clues
    
    def test_puzzle_values_match_solution(self):
        """Test that puzzle values match corresponding solution values."""
        puzzle, solution = sudoku_logic.generate_puzzle()
        
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != sudoku_logic.EMPTY:
                    assert puzzle[i][j] == solution[i][j]
    
    def test_different_puzzles_are_generated(self):
        """Test that multiple calls generate different puzzles."""
        puzzle1, _ = sudoku_logic.generate_puzzle()
        puzzle2, _ = sudoku_logic.generate_puzzle()
        
        # Very unlikely to generate the same puzzle twice
        assert puzzle1 != puzzle2
    
    def test_custom_clue_count(self):
        """Test puzzle generation with different clue counts."""
        for clues in [20, 30, 40, 50]:
            puzzle, solution = sudoku_logic.generate_puzzle(clues=clues)
            clue_count = sum(1 for row in puzzle for cell in row if cell != sudoku_logic.EMPTY)
            assert clue_count == clues
