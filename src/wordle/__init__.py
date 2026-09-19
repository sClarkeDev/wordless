import logging
from collections.abc import Callable
from datetime import date

from wordle.client import WebsiteClient
from wordle.feedback import FeedbackResult, Guess
from wordle.result import RunResult
from wordle.solver import choose_guess

MAX_ATTEMPTS = 6

log = logging.getLogger(__name__)


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
        log.info("Loaded %d words", len(words))
        while len(history) < MAX_ATTEMPTS:
            attempt = len(history) + 1
            word = choose_guess(words, history, tried_words)
            if word is None:
                log.warning("Solver has no candidate left after %d attempts", len(history))
                break

            log.info("Attempt %d: guessing %s", attempt, word)
            tried_words.add(word)

            if on_attempt_start:
                on_attempt_start(attempt, word)
            if not client.submit_guess(word, attempt):
                # Rejected by the game: it's already in tried_words, so pick another.
                log.warning("Game rejected %s; choosing another word", word)
                continue

            feedback = client.read_feedback(attempt)
            log.info("Attempt %d feedback: %s", attempt, [f.name for f in feedback])
            history.append((word, feedback))
            if on_attempt_end:
                on_attempt_end(attempt, word, feedback)

            if feedback == [FeedbackResult.HIT] * 5:
                return finish(won=True, solved_word=word)

        return finish(won=False)
    finally:
        client.close()
