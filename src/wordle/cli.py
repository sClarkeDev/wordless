import contextlib

from rich.console import Console

from wordle import run
from wordle.feedback import FeedbackResult
from wordle.result import format_guess


def main() -> None:
    console = Console()
    try:
        solve(console)
    except Exception as error:
        console.print(f"[red]Error:[/red] {error}")
    finally:
        wait_for_exit(console)


def solve(console: Console) -> None:
    with console.status("Starting...") as status:

        def on_status(message: str) -> None:
            status.update(message)

        def on_attempt_start(attempt: int, word: str) -> None:
            status.update(f"Attempt {attempt}: {word.upper()}")

        def on_attempt_end(attempt: int, word: str, feedback: list[FeedbackResult]) -> None:
            console.print(f"Attempt {attempt}: {format_guess(word, feedback)}")

        result = run(
            on_status=on_status,
            on_attempt_start=on_attempt_start,
            on_attempt_end=on_attempt_end,
        )

    if not result.won:
        console.print("Could not solve the puzzle")


def wait_for_exit(console: Console) -> None:
    with contextlib.suppress(EOFError):
        console.input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
