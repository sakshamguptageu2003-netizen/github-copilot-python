SIZE = 9
EMPTY = 0


def is_safe(board, row, col, num):
    """Return True when placing num at (row, col) does not violate Sudoku rules."""
    if not 1 <= num <= SIZE:
        return False

    for x in range(SIZE):
        if board[row][x] == num or board[x][col] == num:
            return False

    start_row = row - row % 3
    start_col = col - col % 3
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False

    return True
