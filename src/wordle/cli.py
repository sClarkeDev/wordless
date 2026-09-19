import argparse

from rich.console import Console

from wordle import run
from wordle.feedback import FeedbackResult
from wordle.result import format_guess


def main() -> None:
    args = parse_args()
    console = Console()
    with console.status("Starting...") as status:

        def on_status(message: str) -> None:
            status.update(message)

        def on_attempt_start(attempt: int, word: str) -> None:
            status.update(f"Attempt {attempt}: trying [bold]{word.upper()}[/bold]")

        def on_attempt_end(attempt: int, word: str, feedback: list[FeedbackResult]) -> None:
            console.print(f"Attempt {attempt}: {format_guess(word, feedback)}")

        result = run(
            headless=args.headless,
            on_status=on_status,
            on_attempt_start=on_attempt_start,
            on_attempt_end=on_attempt_end if args.headless else None,
        )

    if result.won:
        console.print(f"Solved in {result.attempts} attempts: {result.solved_word}")
    else:
        console.print(f"Not solved after {result.attempts} attempts")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solve today's Wordle automatically.")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser headless instead of showing it.",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
