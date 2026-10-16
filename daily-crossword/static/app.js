const subjectSelect = document.querySelector("#subject");
const gridElement = document.querySelector("#crossword-grid");
const acrossClues = document.querySelector("#across-clues");
const downClues = document.querySelector("#down-clues");
const messageElement = document.querySelector("#game-message");
const checkButton = document.querySelector("#check-button");
const clearButton = document.querySelector("#clear-button");

let puzzle;
let letters = {};
let activeEntryId = "A2";
let activeCell;
let correctEntries = new Set();

function cellKey(cell) {
  return `${cell.row},${cell.column}`;
}

function activeEntry() {
  return puzzle.entries.find((entry) => entry.id === activeEntryId);
}

function setMessage(message) {
  messageElement.textContent = message;
}

function renderGrid() {
  gridElement.replaceChildren();
  puzzle.board.forEach((row) => {
    row.forEach((cell) => {
      if (cell === null) {
        const block = document.createElement("div");
        block.className = "cell cell--block";
        block.setAttribute("aria-hidden", "true");
        gridElement.append(block);
        return;
      }

      const key = cellKey(cell);
      const button = document.createElement("button");
      button.type = "button";
      button.className = "cell";
      button.dataset.cell = key;
      button.setAttribute("aria-label", letters[key]
        ? `Row ${cell.row + 1}, column ${cell.column + 1}: ${letters[key]}`
        : `Row ${cell.row + 1}, column ${cell.column + 1}`);

      if (cell.number !== null) {
        const number = document.createElement("span");
        number.className = "cell-number";
        number.textContent = cell.number;
        button.append(number);
      }

      const letter = document.createElement("span");
      letter.className = "cell-letter";
      letter.textContent = letters[key] || "";
      button.append(letter);

      const entriesForCell = puzzle.entries.filter((entry) =>
        entry.cells.some((entryCell) => cellKey(entryCell) === key));
      if (entriesForCell.some((entry) => entry.id === activeEntryId)) {
        button.classList.add("cell--active-word");
      }
      if (activeCell && cellKey(activeCell) === key) {
        button.classList.add("cell--selected");
      }
      if (entriesForCell.some((entry) => correctEntries.has(entry.id))) {
        button.classList.add("cell--correct");
      }

      button.addEventListener("click", () => selectCell(cell));
      gridElement.append(button);
    });
  });
}

function renderClues() {
  acrossClues.replaceChildren();
  downClues.replaceChildren();

  puzzle.entries.forEach((entry) => {
    const list = entry.direction === "across" ? acrossClues : downClues;
    const item = document.createElement("li");
    const button = document.createElement("button");
    button.type = "button";
    button.className = "clue";
    button.classList.toggle("clue--active", entry.id === activeEntryId);
    button.classList.toggle("clue--correct", correctEntries.has(entry.id));

    const number = document.createElement("span");
    number.className = "clue-number";
    number.textContent = `${entry.number}.`;
    button.append(number, document.createTextNode(entry.clue));
    button.addEventListener("click", () => selectEntry(entry));
    item.append(button);
    list.append(item);
  });
}

function render() {
  renderGrid();
  renderClues();
}

function selectEntry(entry, cell = entry.cells[0]) {
  activeEntryId = entry.id;
  activeCell = cell;
  render();
}

function selectCell(cell) {
  const key = cellKey(cell);
  const matchingEntries = puzzle.entries.filter((entry) =>
    entry.cells.some((entryCell) => cellKey(entryCell) === key));
  if (matchingEntries.length === 0) return;

  const currentlySelected = matchingEntries.find((entry) => entry.id === activeEntryId);
  const nextEntry = currentlySelected && matchingEntries.length > 1
    ? matchingEntries.find((entry) => entry.id !== activeEntryId)
    : currentlySelected || matchingEntries[0];
  selectEntry(nextEntry, cell);
}

function moveWithinEntry(step) {
  const cells = activeEntry().cells;
  const currentIndex = cells.findIndex((cell) => cellKey(cell) === cellKey(activeCell));
  const nextIndex = currentIndex + step;
  if (nextIndex >= 0 && nextIndex < cells.length) {
    activeCell = cells[nextIndex];
    render();
  }
}

function toggleDirection() {
  const key = cellKey(activeCell);
  const crossing = puzzle.entries.find((entry) =>
    entry.id !== activeEntryId
    && entry.cells.some((cell) => cellKey(cell) === key));
  if (crossing) selectEntry(crossing, activeCell);
}

function setLetter(letter) {
  letters[cellKey(activeCell)] = letter;
  correctEntries.clear();
  moveWithinEntry(1);
  render();
}

function handleKeydown(event) {
  if (!puzzle || event.metaKey || event.ctrlKey || event.altKey) return;
  if (document.activeElement === subjectSelect) return;
  if (event.target.closest(".clue, #check-button, #clear-button")) return;

  if (/^[a-z]$/i.test(event.key)) {
    event.preventDefault();
    setLetter(event.key.toUpperCase());
    return;
  }

  if (event.key === "Backspace") {
    event.preventDefault();
    const key = cellKey(activeCell);
    if (letters[key]) {
      delete letters[key];
      correctEntries.clear();
      render();
    } else {
      moveWithinEntry(-1);
      delete letters[cellKey(activeCell)];
      correctEntries.clear();
      render();
    }
    return;
  }

  if (event.key === "Enter") {
    event.preventDefault();
    toggleDirection();
    return;
  }

  const direction = activeEntry().direction;
  const movement = {
    ArrowLeft: [-1, 0],
    ArrowRight: [1, 0],
    ArrowUp: [0, -1],
    ArrowDown: [0, 1],
  }[event.key];
  if (!movement) return;

  event.preventDefault();
  const [columnStep, rowStep] = movement;
  const target = {
    row: activeCell.row + rowStep,
    column: activeCell.column + columnStep,
  };
  const hasCell = puzzle.board[target.row]?.[target.column] !== null
    && puzzle.board[target.row]?.[target.column] !== undefined;
  if (hasCell) {
    const nextEntry = puzzle.entries.find((entry) =>
      entry.direction === direction
      && entry.cells.some((cell) => cellKey(cell) === cellKey(target)));
    if (nextEntry) selectEntry(nextEntry, target);
  }
}

async function loadPuzzle(subject) {
  setMessage("Loading puzzle…");
  const query = subject ? `?subject=${encodeURIComponent(subject)}` : "";
  const response = await fetch(`/api/puzzle${query}`);
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "Could not load the puzzle.");

  puzzle = data;
  letters = {};
  correctEntries = new Set();
  activeEntryId = "A2";
  activeCell = puzzle.entries.find((entry) => entry.id === activeEntryId).cells[0];
  subjectSelect.value = puzzle.subject;
  document.querySelector("#puzzle-date").textContent = puzzle.date;
  document.querySelector("#suggestion").textContent =
    `Today's suggested subject: ${puzzle.suggested_subject}`;
  render();
  setMessage("Select a square and type. At a crossing, press Enter to switch direction.");
}

async function checkPuzzle() {
  checkButton.disabled = true;
  setMessage("Checking your answers…");
  const answers = Object.fromEntries(puzzle.entries.map((entry) => [
    entry.id,
    entry.cells.map((cell) => letters[cellKey(cell)] || "").join(""),
  ]));

  try {
    const response = await fetch("/api/check", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ subject: puzzle.subject, answers }),
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.error || "Could not check the puzzle.");

    correctEntries = new Set(result.correct);
    render();
    if (result.solved) {
      setMessage("Puzzle solved. Nicely done!");
    } else {
      setMessage(`${result.correct.length} of ${puzzle.entries.length} answers are correct. Keep going!`);
    }
  } catch (error) {
    setMessage(error.message);
  } finally {
    checkButton.disabled = false;
  }
}

subjectSelect.addEventListener("change", () => {
  loadPuzzle(subjectSelect.value).catch((error) => setMessage(error.message));
});
checkButton.addEventListener("click", checkPuzzle);
clearButton.addEventListener("click", () => {
  letters = {};
  correctEntries.clear();
  render();
  setMessage("Letters cleared.");
});
window.addEventListener("keydown", handleKeydown);

loadPuzzle().catch((error) => setMessage(error.message));
