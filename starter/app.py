from flask import Flask, render_template, jsonify, request
import sudoku_logic

app = Flask(__name__)

DIFFICULTY_CLUES = {
    'easy': 45,
    'medium': 35,
    'hard': 25,
}

# Keep a simple in-memory store for current puzzle and solution
CURRENT = {
    'puzzle': None,
    'solution': None
}


def resolve_clues():
    clues_param = request.args.get('clues')
    if clues_param is not None:
        return int(clues_param)

    difficulty = (request.args.get('difficulty', 'medium') or 'medium').lower()
    return DIFFICULTY_CLUES.get(difficulty, DIFFICULTY_CLUES['medium'])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/new')
def new_game():
    clues = resolve_clues()
    puzzle, solution = sudoku_logic.generate_puzzle(clues)
    CURRENT['puzzle'] = puzzle
    CURRENT['solution'] = solution
    return jsonify({'puzzle': puzzle})

@app.route('/hint', methods=['POST'])
def get_hint():
    data = request.json or {}
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    if not isinstance(board, list) or len(board) != sudoku_logic.SIZE:
        return jsonify({'error': 'Invalid board'}), 400

    for i in range(sudoku_logic.SIZE):
        if not isinstance(board[i], list) or len(board[i]) != sudoku_logic.SIZE:
            return jsonify({'error': 'Invalid board'}), 400

    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] == 0:
                return jsonify({'row': i, 'col': j, 'value': solution[i][j]})

    return jsonify({'error': 'No empty cells remain'}), 400


@app.route('/check', methods=['POST'])
def check_solution():
    data = request.json
    board = data.get('board')
    solution = CURRENT.get('solution')
    if solution is None:
        return jsonify({'error': 'No game in progress'}), 400
    incorrect = []
    for i in range(sudoku_logic.SIZE):
        for j in range(sudoku_logic.SIZE):
            if board[i][j] != solution[i][j]:
                incorrect.append([i, j])
    return jsonify({'incorrect': incorrect})

if __name__ == '__main__':
    app.run(debug=True)
