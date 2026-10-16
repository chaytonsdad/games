"""Curated mini crossword puzzles and their daily selection."""

from datetime import date
from typing import Dict, Optional, Set, Tuple


class Puzzle:
    def __init__(
        self,
        subject: str,
        across: str,
        down_left: str,
        down_right: str,
        clues: Tuple[str, str, str],
    ) -> None:
        self.subject = subject
        self.across = across.upper()
        self.down_left = down_left.upper()
        self.down_right = down_right.upper()
        self.clues = clues

        if any(
            len(answer) != 3
            for answer in (self.across, self.down_left, self.down_right)
        ):
            raise ValueError("Starter puzzles use three-letter answers.")
        if self.down_left[1] != self.across[0]:
            raise ValueError("The left Down answer must cross the Across answer.")
        if self.down_right[1] != self.across[2]:
            raise ValueError("The right Down answer must cross the Across answer.")

    def entries(self) -> Dict[str, str]:
        return {
            "A2": self.across,
            "D1": self.down_left,
            "D3": self.down_right,
        }

    def clue_text(self) -> Dict[str, str]:
        return dict(zip(("A2", "D1", "D3"), self.clues))

    def entry_cells(self) -> Dict[str, Tuple[Tuple[int, int], ...]]:
        return {
            "A2": tuple((1, column) for column in range(3)),
            "D1": tuple((row, 0) for row in range(3)),
            "D3": tuple((row, 2) for row in range(3)),
        }


PUZZLES = {
    "Animals": (
        Puzzle(
            "Animals",
            "CAT",
            "ACE",
            "ATE",
            (
                "A small, furry pet that purrs",
                "A playing card with a single mark",
                "Had a meal",
            ),
        ),
        Puzzle(
            "Animals",
            "HEN",
            "WHO",
            "ANT",
            (
                "A female chicken",
                "A question asking which person",
                "A tiny insect known for teamwork",
            ),
        ),
    ),
    "Food": (
        Puzzle(
            "Food",
            "PIE",
            "APE",
            "PEA",
            (
                "A baked dish with a crust",
                "A large primate",
                "A small green vegetable",
            ),
        ),
        Puzzle(
            "Food",
            "EAT",
            "PEA",
            "ATE",
            (
                "What you do at a meal",
                "A small green vegetable",
                "Finished a meal",
            ),
        ),
    ),
    "Nature": (
        Puzzle(
            "Nature",
            "SUN",
            "ASH",
            "ANT",
            (
                "The star at the center of our solar system",
                "A tree whose wood is often used for tools",
                "A tiny insect known for teamwork",
            ),
        ),
        Puzzle(
            "Nature",
            "AIR",
            "MAP",
            "ORB",
            (
                "The mixture of gases around Earth",
                "A drawing that helps you find a place",
                "A round object",
            ),
        ),
    ),
    "Sports": (
        Puzzle(
            "Sports",
            "HIT",
            "WHO",
            "ATE",
            (
                "A successful contact with a ball in baseball",
                "A question asking which person",
                "Finished a meal",
            ),
        ),
        Puzzle(
            "Sports",
            "RUN",
            "ARM",
            "ONE",
            (
                "Move quickly on foot",
                "A body part used to throw a ball",
                "The number after zero",
            ),
        ),
    ),
}


def suggested_subject(today: Optional[date] = None) -> str:
    """Pick a stable subject for the current day."""
    topics = list(PUZZLES)
    day = today or date.today()
    return topics[day.toordinal() % len(topics)]


def puzzle_for_day(subject: str, today: Optional[date] = None) -> Puzzle:
    """Select a subject's daily puzzle in a repeatable way."""
    day = today or date.today()
    puzzles = PUZZLES[subject]
    return puzzles[day.toordinal() % len(puzzles)]


def render_grid(puzzle: Puzzle, solved: Set[str]) -> str:
    entries = puzzle.entries()
    positions = puzzle.entry_cells()
    visible: Dict[Tuple[int, int], str] = {}

    for entry_id in solved:
        for position, letter in zip(positions[entry_id], entries[entry_id]):
            visible[position] = letter

    rows = []
    for row in range(3):
        cells = []
        for column in range(3):
            if (row, column) in ((0, 1), (2, 1)):
                cells.append("#")
            else:
                cells.append(visible.get((row, column), "."))
        rows.append(" ".join(cells))
    return "\n".join(rows)


if __name__ == "__main__":
    from webapp import run

    run()
