import unittest
from datetime import date, timedelta

from main import PUZZLES, puzzle_for_day, render_grid, suggested_subject
from webapp import check_answers, puzzle_payload


class CrosswordPuzzleTests(unittest.TestCase):
    def test_every_entry_has_a_matching_crossing_letter(self):
        for puzzles in PUZZLES.values():
            for puzzle in puzzles:
                self.assertEqual(puzzle.down_left[1], puzzle.across[0])
                self.assertEqual(puzzle.down_right[1], puzzle.across[2])
                self.assertEqual(len(set(puzzle.entries().values())), 3)

    def test_grid_reveals_letters_from_solved_entries(self):
        puzzle = PUZZLES["Animals"][0]
        self.assertEqual(render_grid(puzzle, {"A2", "D3"}), ". # A\nC A T\n. # E")

    def test_suggested_subject_is_stable_for_the_day(self):
        today = date(2026, 10, 16)
        expected = list(PUZZLES)[today.toordinal() % len(PUZZLES)]
        self.assertEqual(suggested_subject(today), expected)

    def test_subject_puzzle_rotates_daily(self):
        today = date(2026, 10, 16)
        for subject in PUZZLES:
            self.assertNotEqual(
                puzzle_for_day(subject, today),
                puzzle_for_day(subject, today + timedelta(days=1)),
            )

    def test_web_payload_has_numbered_clues_without_answers(self):
        payload = puzzle_payload("Animals", date(2026, 10, 16))
        self.assertEqual(payload["subject"], "Animals")
        self.assertEqual(
            [(entry["id"], entry["number"]) for entry in payload["entries"]],
            [("A2", 2), ("D1", 1), ("D3", 3)],
        )
        self.assertNotIn("answer", payload["entries"][0])
        self.assertEqual(payload["board"][0][1], None)

    def test_check_answers_reports_correct_entries(self):
        puzzle = PUZZLES["Animals"][0]
        result = check_answers(puzzle, {"A2": "cat", "D1": "ACE", "D3": "ATE"})
        self.assertEqual(set(result["correct"]), {"A2", "D1", "D3"})
        self.assertTrue(result["solved"])

    def test_check_answers_rejects_unknown_entries(self):
        with self.assertRaises(ValueError):
            check_answers(PUZZLES["Animals"][0], {"A1": "CAT"})


if __name__ == "__main__":
    unittest.main()
