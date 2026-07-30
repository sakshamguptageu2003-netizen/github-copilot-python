import pytest
import json
import app as app_module


class TestIndexRoute:
    """Tests for the index route."""
    
    def test_index_returns_200(self, client):
        """Test that index route returns a 200 status code."""
        response = client.get('/')
        assert response.status_code == 200
    
    def test_index_returns_html(self, client):
        """Test that index route returns HTML content."""
        response = client.get('/')
        assert response.content_type == 'text/html; charset=utf-8'

    def test_index_includes_timer_display(self, client):
        """Test that the index page includes a timer display element."""
        response = client.get('/')
        assert b'id="timer-display"' in response.data

    def test_index_includes_check_button(self, client):
        """Test that the index page includes a Check button."""
        response = client.get('/')
        assert b'>Check<' in response.data

    def test_index_includes_leaderboard_elements(self, client):
        """Test that the index page includes leaderboard controls and list."""
        response = client.get('/')
        assert b'id="leaderboard"' in response.data
        assert b'id="player-name"' in response.data
        assert b'id="save-score"' in response.data

    def test_index_includes_theme_toggle(self, client):
        """Test that the index page includes a theme toggle control."""
        response = client.get('/')
        assert b'id="theme-toggle"' in response.data


class TestNewGameRoute:
    """Tests for the new game endpoint."""
    
    def test_new_game_returns_200(self, client):
        """Test that /new route returns a 200 status code."""
        response = client.get('/new')
        assert response.status_code == 200
    
    def test_new_game_returns_json(self, client):
        """Test that /new route returns JSON."""
        response = client.get('/new')
        assert response.content_type == 'application/json'
    
    def test_new_game_returns_puzzle(self, client):
        """Test that /new route returns a puzzle in the response."""
        response = client.get('/new')
        data = json.loads(response.data)
        
        assert 'puzzle' in data
        assert isinstance(data['puzzle'], list)
        assert len(data['puzzle']) == 9
    
    def test_new_game_puzzle_is_9x9(self, client):
        """Test that returned puzzle is a valid 9x9 board."""
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        assert all(len(row) == 9 for row in puzzle)
    
    def test_new_game_stores_puzzle_and_solution(self, client):
        """Test that new game stores puzzle and solution in CURRENT."""
        # Ensure CURRENT is empty before the request
        app_module.CURRENT['puzzle'] = None
        app_module.CURRENT['solution'] = None
        
        response = client.get('/new')
        
        assert app_module.CURRENT['puzzle'] is not None
        assert app_module.CURRENT['solution'] is not None
    
    def test_new_game_with_custom_clues(self, client):
        """Test that /new route accepts custom clue count."""
        response = client.get('/new?clues=50')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 50
    
    def test_new_game_default_clues(self, client):
        """Test that /new route uses default clue count (35)."""
        response = client.get('/new')
        data = json.loads(response.data)
        puzzle = data['puzzle']
        
        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 35

    def test_new_game_easy_difficulty_uses_45_clues(self, client):
        """Test that /new?difficulty=easy uses 45 clues."""
        response = client.get('/new?difficulty=easy')
        data = json.loads(response.data)
        puzzle = data['puzzle']

        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 45

    def test_new_game_hard_difficulty_uses_25_clues(self, client):
        """Test that /new?difficulty=hard uses 25 clues."""
        response = client.get('/new?difficulty=hard')
        data = json.loads(response.data)
        puzzle = data['puzzle']

        clue_count = sum(1 for row in puzzle for cell in row if cell != 0)
        assert clue_count == 25
    
    def test_multiple_new_games_overwrite_previous(self, client):
        """Test that calling /new multiple times overwrites the previous game."""
        response1 = client.get('/new')
        puzzle1 = json.loads(response1.data)['puzzle']
        
        response2 = client.get('/new')
        puzzle2 = json.loads(response2.data)['puzzle']
        
        # Verify that a new puzzle was generated (very unlikely to be identical)
        assert puzzle1 != puzzle2
        # Verify that CURRENT now stores the second puzzle
        assert app_module.CURRENT['puzzle'] == puzzle2


class TestCheckSolutionRoute:
    """Tests for the check solution endpoint."""
    
    def test_check_requires_post(self, client):
        """Test that /check requires POST method."""
        response = client.get('/check')
        assert response.status_code == 405  # Method Not Allowed
    
    def test_check_without_game_in_progress(self, client):
        """Test that /check returns error when no game is in progress."""
        app_module.CURRENT['puzzle'] = None
        app_module.CURRENT['solution'] = None
        
        response = client.post('/check', 
                             json={'board': [[0]*9 for _ in range(9)]},
                             content_type='application/json')
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_check_with_correct_solution(self, client):
        """Test that /check identifies a correct solution."""
        # Create a new game first
        client.get('/new')
        solution = app_module.CURRENT['solution']
        
        response = client.post('/check',
                             json={'board': solution},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
        assert len(data['incorrect']) == 0
    
    def test_check_with_incorrect_solution(self, client):
        """Test that /check identifies incorrect cells."""
        # Create a new game first
        client.get('/new')
        solution = app_module.CURRENT['solution']
        
        # Create an incorrect board (change first cell)
        incorrect_board = [row[:] for row in solution]
        original_value = incorrect_board[0][0]
        # Set to a different value
        new_value = (original_value % 9) + 1
        incorrect_board[0][0] = new_value
        
        response = client.post('/check',
                             json={'board': incorrect_board},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'incorrect' in data
        assert [0, 0] in data['incorrect']
    
    def test_check_with_multiple_errors(self, client):
        """Test that /check reports multiple incorrect cells."""
        # Create a new game first
        client.get('/new')
        solution = app_module.CURRENT['solution']
        
        # Create an incorrect board (change multiple cells)
        incorrect_board = [row[:] for row in solution]
        incorrect_board[0][0] = (solution[0][0] % 9) + 1
        incorrect_board[1][1] = (solution[1][1] % 9) + 1
        incorrect_board[2][2] = (solution[2][2] % 9) + 1
        
        response = client.post('/check',
                             json={'board': incorrect_board},
                             content_type='application/json')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['incorrect']) >= 3
    
    def test_check_response_format(self, client):
        """Test that /check response has correct JSON format."""
        client.get('/new')
        solution = app_module.CURRENT['solution']
        
        response = client.post('/check',
                             json={'board': solution},
                             content_type='application/json')
        
        data = json.loads(response.data)
        assert isinstance(data['incorrect'], list)
        # Each incorrect cell should be a [row, col] pair
        for cell in data['incorrect']:
            assert isinstance(cell, list)
            assert len(cell) == 2
            assert all(isinstance(idx, int) for idx in cell)


class TestHintRoute:
    """Tests for the hint endpoint."""

    def test_hint_returns_one_correct_empty_cell(self, client):
        """Test that /hint returns one valid hint for an empty cell."""
        client.get('/new')
        board = [row[:] for row in app_module.CURRENT['puzzle']]

        response = client.post('/hint', json={'board': board}, content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert {'row', 'col', 'value'}.issubset(set(data.keys()))
        assert 0 <= data['row'] < 9
        assert 0 <= data['col'] < 9
        assert 1 <= data['value'] <= 9
        assert board[data['row']][data['col']] == 0
        assert data['value'] == app_module.CURRENT['solution'][data['row']][data['col']]

    def test_hint_does_not_overwrite_existing_user_input(self, client):
        """Test that /hint leaves user-filled cells unchanged."""
        client.get('/new')
        board = [row[:] for row in app_module.CURRENT['puzzle']]
        board[0][0] = 1

        response = client.post('/hint', json={'board': board}, content_type='application/json')

        assert response.status_code == 200
        data = json.loads(response.data)
        assert not (data['row'] == 0 and data['col'] == 0)
        assert board[0][0] == 1


class TestGameFlow:
    """Tests for typical game flow scenarios."""
    
    def test_complete_game_flow(self, client):
        """Test a complete game: create puzzle, check partial solution, then complete solution."""
        # 1. Create new game
        response = client.get('/new?clues=40')
        puzzle = json.loads(response.data)['puzzle']
        assert sum(1 for row in puzzle for cell in row if cell != 0) == 40
        
        # 2. Get the solution
        solution = app_module.CURRENT['solution']
        
        # 3. Check correct solution
        response = client.post('/check',
                             json={'board': solution},
                             content_type='application/json')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data['incorrect']) == 0
    
    def test_puzzle_and_solution_consistency(self, client):
        """Test that puzzle clues are all present in the solution."""
        response = client.get('/new')
        puzzle = json.loads(response.data)['puzzle']
        solution = app_module.CURRENT['solution']
        
        # Every clue in the puzzle should match the solution
        for i in range(9):
            for j in range(9):
                if puzzle[i][j] != 0:
                    assert puzzle[i][j] == solution[i][j]
