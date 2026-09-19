from collections.abc import Callable
from datetime import date

from wordle.client import WebsiteClient
from wordle.feedback import FeedbackResult, Guess
from wordle.result import RunResult
from wordle.solver import choose_guess

MAX_ATTEMPTS = 6


def run(
    headless: bool = False,
    on_status: Callable[[str], None] | None = None,
    on_attempt_start: Callable[[int, str], None] | None = None,
    on_attempt_end: Callable[[int, str, list[FeedbackResult]], None] | None = None,
) -> RunResult:
    run_date = date.today()
    client = WebsiteClient(headless=headless)
    history: list[Guess] = []
    tried_words: set[str] = set()

    def finish(won: bool, solved_word: str | None = None) -> RunResult:
        return RunResult(
            date=run_date, won=won, attempts=len(history), guesses=history, solved_word=solved_word
        )

    try:
        client.open(on_status)
        words = client.fetch_words()
        while len(history) < MAX_ATTEMPTS:
            attempt = len(history) + 1
            word = choose_guess(words, history, tried_words)
            if word is None:
                break

            tried_words.add(word)

            if on_attempt_start:
                on_attempt_start(attempt, word)
            if not client.submit_guess(word, attempt):
                # Rejected by the game: it's already in tried_words, so pick another.
                continue

            feedback = client.read_feedback(attempt)
            history.append((word, feedback))
            if on_attempt_end:
                on_attempt_end(attempt, word, feedback)

            if feedback == [FeedbackResult.HIT] * 5:
                return finish(won=True, solved_word=word)

        return finish(won=False)
    finally:
        client.close()
