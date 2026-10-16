"""Local HTTP app for the Daily Crossword."""

from datetime import date
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
from pathlib import Path
import re
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlsplit
import webbrowser

from main import PUZZLES, Puzzle, puzzle_for_day, suggested_subject


HOST = "127.0.0.1"
PORT = 8000
STATIC_DIR = Path(__file__).parent / "static"
MAX_REQUEST_SIZE = 4096


def puzzle_payload(subject: Optional[str] = None, today: Optional[date] = None) -> Dict[str, Any]:
    day = today or date.today()
    selected_subject = subject or suggested_subject(day)
    if selected_subject not in PUZZLES:
        raise ValueError("Unknown crossword subject.")

    puzzle = puzzle_for_day(selected_subject, day)
    numbers = {"0,0": 1, "1,0": 2, "0,2": 3}
    board = []
    for row in range(3):
        board_row = []
        for column in range(3):
            if (row, column) in ((0, 1), (2, 1)):
                board_row.append(None)
            else:
                board_row.append({
                    "number": numbers.get("{},{}".format(row, column)),
                    "row": row,
                    "column": column,
                })
        board.append(board_row)

    entries = []
    for entry_id in puzzle.entries():
        entries.append({
            "id": entry_id,
            "direction": "across" if entry_id.startswith("A") else "down",
            "number": int(entry_id[1:]),
            "clue": puzzle.clue_text()[entry_id],
            "cells": [
                {"row": row, "column": column}
                for row, column in puzzle.entry_cells()[entry_id]
            ],
        })

    return {
        "subject": selected_subject,
        "suggested_subject": suggested_subject(day),
        "date": day.strftime("%A, %B %-d, %Y"),
        "board": board,
        "entries": entries,
    }


def check_answers(
    puzzle: Puzzle,
    answers: Dict[str, str],
) -> Dict[str, Any]:
    puzzle_entries = puzzle.entries()
    if any(entry_id not in puzzle_entries for entry_id in answers):
        raise ValueError("Unknown crossword entry.")
    if any(
        not isinstance(answer, str)
        or re.fullmatch(r"[A-Za-z]{0,3}", answer) is None
        for answer in answers.values()
    ):
        raise ValueError("Each answer must contain at most three letters.")

    correct = [
        entry_id
        for entry_id, answer in answers.items()
        if answer.upper() == puzzle_entries[entry_id]
    ]
    return {
        "correct": correct,
        "solved": len(correct) == len(puzzle_entries),
    }


class CrosswordHandler(BaseHTTPRequestHandler):
    def _send_json(self, status: int, payload: Dict[str, Any]) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def _send_file(self, filename: str, content_type: str) -> None:
        body = (STATIC_DIR / filename).read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        request = urlsplit(self.path)
        if request.path == "/":
            self._send_file("index.html", "text/html; charset=utf-8")
            return
        if request.path == "/styles.css":
            self._send_file("styles.css", "text/css; charset=utf-8")
            return
        if request.path == "/app.js":
            self._send_file("app.js", "text/javascript; charset=utf-8")
            return
        if request.path == "/api/puzzle":
            query = parse_qs(request.query)
            subject = query.get("subject", [None])[0]
            try:
                payload = puzzle_payload(subject)
            except ValueError as error:
                self._send_json(400, {"error": str(error)})
                return
            self._send_json(200, payload)
            return
        self._send_json(404, {"error": "Not found."})

    def do_POST(self) -> None:
        if urlsplit(self.path).path != "/api/check":
            self._send_json(404, {"error": "Not found."})
            return

        content_length = self.headers.get("Content-Length", "")
        if not content_length.isdigit():
            self._send_json(400, {"error": "A valid Content-Length is required."})
            return
        if int(content_length) > MAX_REQUEST_SIZE:
            self._send_json(413, {"error": "Request is too large."})
            return

        try:
            request_body = json.loads(self.rfile.read(int(content_length)))
        except (json.JSONDecodeError, UnicodeDecodeError):
            self._send_json(400, {"error": "Request body must be valid JSON."})
            return
        if not isinstance(request_body, dict):
            self._send_json(400, {"error": "Request body must be a JSON object."})
            return

        subject = request_body.get("subject")
        answers = request_body.get("answers")
        if not isinstance(subject, str) or subject not in PUZZLES:
            self._send_json(400, {"error": "Unknown crossword subject."})
            return
        if not isinstance(answers, dict) or any(
            not isinstance(entry_id, str) or not isinstance(answer, str)
            for entry_id, answer in answers.items()
        ):
            self._send_json(400, {"error": "Answers must map clue IDs to text."})
            return

        puzzle = puzzle_for_day(subject)
        try:
            result = check_answers(puzzle, answers)
        except ValueError as error:
            self._send_json(400, {"error": str(error)})
            return
        self._send_json(200, result)

    def log_message(self, format: str, *args: object) -> None:
        print("{} - {}".format(self.address_string(), format % args))


def run() -> None:
    address = "http://{}:{}".format(HOST, PORT)
    server = HTTPServer((HOST, PORT), CrosswordHandler)
    print("Daily Crossword is running at {}".format(address))
    print("Press Control-C to stop the server.")
    webbrowser.open_new_tab(address)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping Daily Crossword.")
    finally:
        server.server_close()


if __name__ == "__main__":
    run()
