// Client-side rendering and interaction for the Flask-backed Sudoku
const SIZE = 9;
const STORAGE_KEY = 'sudoku-leaderboard';
const THEME_STORAGE_KEY = 'sudoku-theme-preference';
let puzzle = [];
let timerInterval = null;
let elapsedSeconds = 0;
let timerRunning = false;
let hintsUsed = 0;
let currentDifficulty = 'medium';
let gameCompleted = false;

function formatTime(totalSeconds) {
  const minutes = String(Math.floor(totalSeconds / 60)).padStart(2, '0');
  const seconds = String(totalSeconds % 60).padStart(2, '0');
  return `${minutes}:${seconds}`;
}

function updateTimerDisplay() {
  document.getElementById('timer-display').innerText = formatTime(elapsedSeconds);
}

function startTimer() {
  clearInterval(timerInterval);
  elapsedSeconds = 0;
  timerRunning = true;
  updateTimerDisplay();
  timerInterval = window.setInterval(() => {
    if (!timerRunning) return;
    elapsedSeconds += 1;
    updateTimerDisplay();
  }, 1000);
}

function stopTimer() {
  timerRunning = false;
  clearInterval(timerInterval);
}

function loadLeaderboard() {
  const raw = window.localStorage.getItem(STORAGE_KEY);
  if (!raw) return [];
  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed : [];
  } catch (error) {
    return [];
  }
}

function saveLeaderboard(entries) {
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify(entries));
}

function renderLeaderboard() {
  const list = document.getElementById('leaderboard');
  if (!list) return;
  const entries = loadLeaderboard().slice().sort((a, b) => {
    if (a.timeSeconds !== b.timeSeconds) {
      return a.timeSeconds - b.timeSeconds;
    }
    return a.hintsUsed - b.hintsUsed;
  }).slice(0, 10);

  if (!entries.length) {
    list.innerHTML = '<li>No scores saved yet.</li>';
    return;
  }

  list.innerHTML = entries.map((entry, index) => {
    const timeText = formatTime(entry.timeSeconds);
    return `<li>#${index + 1} ${entry.playerName || 'Anonymous'} — ${timeText} — ${entry.difficulty} — hints: ${entry.hintsUsed}</li>`;
  }).join('');
}

function isDuplicateLeaderboardEntry(entries, newEntry) {
  return entries.some(entry =>
    entry.playerName === newEntry.playerName &&
    entry.timeSeconds === newEntry.timeSeconds &&
    entry.difficulty === newEntry.difficulty &&
    entry.hintsUsed === newEntry.hintsUsed
  );
}

function addLeaderboardEntry(playerName, timeSeconds, difficulty, hintsUsed) {
  const normalizedName = playerName.trim() || 'Anonymous';
  const newEntry = {
    playerName: normalizedName,
    timeSeconds,
    difficulty,
    hintsUsed
  };

  const entries = loadLeaderboard();
  if (isDuplicateLeaderboardEntry(entries, newEntry)) {
    renderLeaderboard();
    return false;
  }

  entries.push(newEntry);
  const sorted = entries.slice().sort((a, b) => {
    if (a.timeSeconds !== b.timeSeconds) {
      return a.timeSeconds - b.timeSeconds;
    }
    return a.hintsUsed - b.hintsUsed;
  }).slice(0, 10);
  saveLeaderboard(sorted);
  renderLeaderboard();
  return true;
}

function getPreferredTheme() {
  const storedTheme = window.localStorage.getItem(THEME_STORAGE_KEY);
  if (storedTheme === 'dark' || storedTheme === 'light') {
    return storedTheme;
  }

  return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}

function applyTheme(theme) {
  document.body.dataset.theme = theme;
  const toggleButton = document.getElementById('theme-toggle');
  if (toggleButton) {
    toggleButton.textContent = theme === 'dark' ? '☀️ Light Mode' : '🌙 Dark Mode';
    toggleButton.setAttribute('aria-pressed', String(theme === 'dark'));
  }
}

function toggleTheme() {
  const nextTheme = document.body.dataset.theme === 'dark' ? 'light' : 'dark';
  window.localStorage.setItem(THEME_STORAGE_KEY, nextTheme);
  applyTheme(nextTheme);
}

function getCellIndex(row, col) {
  return row * SIZE + col;
}

function getCellBlockClass(row, col) {
  const blockRow = Math.floor(row / 3);
  const blockCol = Math.floor(col / 3);
  return (blockRow + blockCol) % 2 === 0 ? 'block-light' : 'block-dark';
}

function getConflictingCells(board) {
  const conflicts = new Set();

  for (let row = 0; row < SIZE; row += 1) {
    for (let col = 0; col < SIZE; col += 1) {
      const value = board[row][col];
      if (!value) continue;

      const rowMatches = [];
      for (let colIndex = 0; colIndex < SIZE; colIndex += 1) {
        if (colIndex !== col && board[row][colIndex] === value) {
          rowMatches.push(getCellIndex(row, colIndex));
        }
      }

      const colMatches = [];
      for (let rowIndex = 0; rowIndex < SIZE; rowIndex += 1) {
        if (rowIndex !== row && board[rowIndex][col] === value) {
          colMatches.push(getCellIndex(rowIndex, col));
        }
      }

      const boxStartRow = Math.floor(row / 3) * 3;
      const boxStartCol = Math.floor(col / 3) * 3;
      const boxMatches = [];
      for (let boxRow = boxStartRow; boxRow < boxStartRow + 3; boxRow += 1) {
        for (let boxCol = boxStartCol; boxCol < boxStartCol + 3; boxCol += 1) {
          if ((boxRow !== row || boxCol !== col) && board[boxRow][boxCol] === value) {
            boxMatches.push(getCellIndex(boxRow, boxCol));
          }
        }
      }

      if (rowMatches.length || colMatches.length || boxMatches.length) {
        conflicts.add(getCellIndex(row, col));
        rowMatches.forEach((idx) => conflicts.add(idx));
        colMatches.forEach((idx) => conflicts.add(idx));
        boxMatches.forEach((idx) => conflicts.add(idx));
      }
    }
  }

  return conflicts;
}

function refreshConflictHighlights() {
  const boardDiv = document.getElementById('sudoku-board');
  if (!boardDiv) return;

  const inputs = boardDiv.getElementsByTagName('input');
  const conflictingCells = getConflictingCells(puzzle);

  for (let idx = 0; idx < inputs.length; idx += 1) {
    const input = inputs[idx];
    const row = Math.floor(idx / SIZE);
    const col = idx % SIZE;
    const classes = ['sudoku-cell', getCellBlockClass(row, col)];

    if (input.classList.contains('prefilled')) {
      classes.push('prefilled');
    } else if (input.classList.contains('hinted')) {
      classes.push('hinted');
    }

    if (input.classList.contains('incorrect')) {
      classes.push('incorrect');
    }

    if (conflictingCells.has(idx)) {
      classes.push('conflict');
    }

    input.className = classes.join(' ');
  }
}

function createBoardElement() {
  const boardDiv = document.getElementById('sudoku-board');
  boardDiv.innerHTML = '';
  for (let i = 0; i < SIZE; i++) {
    const rowDiv = document.createElement('div');
    rowDiv.className = 'sudoku-row';
    for (let j = 0; j < SIZE; j++) {
      const input = document.createElement('input');
      input.type = 'text';
      input.maxLength = 1;
      input.dataset.row = i;
      input.dataset.col = j;
      input.className = `sudoku-cell ${getCellBlockClass(i, j)}`;
      input.addEventListener('input', (e) => {
        const val = e.target.value.replace(/[^1-9]/g, '');
        e.target.value = val;
        const row = parseInt(e.target.dataset.row, 10);
        const col = parseInt(e.target.dataset.col, 10);
        if (!Number.isNaN(row) && !Number.isNaN(col)) {
          puzzle[row][col] = val ? parseInt(val, 10) : 0;
          refreshConflictHighlights();
        }
      });
      rowDiv.appendChild(input);
    }
    boardDiv.appendChild(rowDiv);
  }
}

function getBoardFromInputs() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = [];
  for (let i = 0; i < SIZE; i++) {
    board[i] = [];
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = inputs[idx].value;
      board[i][j] = val ? parseInt(val, 10) : 0;
    }
  }
  return board;
}

function applyHint(row, col, value) {
  const idx = row * SIZE + col;
  const boardDiv = document.getElementById('sudoku-board');
  const input = boardDiv.getElementsByTagName('input')[idx];
  input.value = value;
  input.disabled = true;
  input.className = `sudoku-cell ${getCellBlockClass(row, col)} hinted`;
  puzzle[row][col] = value;
  refreshConflictHighlights();
}

function renderPuzzle(puz) {
  puzzle = puz;
  hintsUsed = 0;
  gameCompleted = false;
  createBoardElement();
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  for (let i = 0; i < SIZE; i++) {
    for (let j = 0; j < SIZE; j++) {
      const idx = i * SIZE + j;
      const val = puzzle[i][j];
      const inp = inputs[idx];
      const blockClass = getCellBlockClass(i, j);
      if (val !== 0) {
        inp.value = val;
        inp.disabled = true;
        inp.className = `sudoku-cell ${blockClass} prefilled`;
      } else {
        inp.value = '';
        inp.disabled = false;
        inp.className = `sudoku-cell ${blockClass}`;
      }
    }
  }
  refreshConflictHighlights();
}

async function newGame() {
  stopTimer();
  currentDifficulty = document.getElementById('difficulty-select').value;
  const res = await fetch(`/new?difficulty=${encodeURIComponent(currentDifficulty)}`);
  const data = await res.json();
  renderPuzzle(data.puzzle);
  document.getElementById('message').innerText = '';
  startTimer();
}

async function requestHint() {
  const board = getBoardFromInputs();
  const res = await fetch('/hint', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  hintsUsed += 1;
  applyHint(data.row, data.col, data.value);
  msg.style.color = '#1976d2';
  msg.innerText = 'Hint revealed a correct value.';
}

async function checkSolution() {
  const boardDiv = document.getElementById('sudoku-board');
  const inputs = boardDiv.getElementsByTagName('input');
  const board = getBoardFromInputs();
  const res = await fetch('/check', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({board})
  });
  const data = await res.json();
  const msg = document.getElementById('message');
  if (data.error) {
    msg.style.color = '#d32f2f';
    msg.innerText = data.error;
    return;
  }
  const incorrect = new Set(data.incorrect.map(x => x[0]*SIZE + x[1]));
  for (let idx = 0; idx < inputs.length; idx++) {
    const inp = inputs[idx];
    if (inp.disabled) continue;
    const row = Math.floor(idx / SIZE);
    const col = idx % SIZE;
    inp.className = `sudoku-cell ${getCellBlockClass(row, col)}`;
    if (incorrect.has(idx)) {
      inp.className = `sudoku-cell ${getCellBlockClass(row, col)} incorrect`;
    }
  }
  refreshConflictHighlights();
  if (incorrect.size === 0) {
    stopTimer();
    gameCompleted = true;
    msg.style.color = '#388e3c';
    msg.innerText = 'Congratulations! You solved it!';
  } else {
    msg.style.color = '#d32f2f';
    msg.innerText = 'Some cells are incorrect.';
  }
}

function saveScore() {
  if (!gameCompleted) {
    const msg = document.getElementById('message');
    msg.style.color = '#d32f2f';
    msg.innerText = 'Finish a game before saving a score.';
    return;
  }

  const nameInput = document.getElementById('player-name');
  const playerName = nameInput ? nameInput.value : '';
  const saved = addLeaderboardEntry(playerName, elapsedSeconds, currentDifficulty, hintsUsed);

  const msg = document.getElementById('message');
  if (saved) {
    msg.style.color = '#388e3c';
    msg.innerText = 'Score saved to the leaderboard.';
  } else {
    msg.style.color = '#1976d2';
    msg.innerText = 'This score is already on the leaderboard.';
  }
}

// Wire buttons
window.addEventListener('load', () => {
  applyTheme(getPreferredTheme());
  document.getElementById('new-game').addEventListener('click', newGame);
  document.getElementById('check-solution').addEventListener('click', checkSolution);
  document.getElementById('hint').addEventListener('click', requestHint);
  document.getElementById('save-score').addEventListener('click', saveScore);
  document.getElementById('theme-toggle').addEventListener('click', toggleTheme);
  renderLeaderboard();
  // initialize
  newGame();
});
