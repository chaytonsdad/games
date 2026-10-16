# Daily Crossword

A local, browser-based mini crossword written in Python and plain HTML, CSS, and
JavaScript. It uses only Python's standard library; there are no packages to
install, and the app does not need an internet connection.

## Start the game

In Terminal (zsh is fine), run:

```zsh
cd /Users/mw/Coding/daily-crossword
python3 main.py
```

The app opens in your browser at <http://127.0.0.1:8000>. Keep the Terminal
window open while playing; press **Control-C** there to stop the local server.

## Play

- Choose a subject or use the daily suggested subject.
- Click a clue or a square, then type letters. The selected answer and its
  crossing squares are highlighted.
- Use the arrow keys to move between squares. At a crossing, press **Enter**
  to switch between Across and Down.
- Choose **Check puzzle** to see which answers are correct, or **Clear letters**
  to start over.

The starter game has a small 3-by-3 mini-crossword layout and two curated
puzzles for each of four subjects. The daily puzzle rotates through those
puzzles. Answers are checked locally by the Python app; the browser UI does not
receive the answer key. Letters are kept only in the current page, so refreshing
the browser clears the in-progress grid.

## Run the tests

```zsh
python3 -m unittest discover -s tests -v
```
