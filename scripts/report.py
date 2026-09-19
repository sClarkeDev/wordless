from pathlib import Path

from storage import RESULTS_PATH, load_history

from wordle.result import RunResult

README_PATH = Path(__file__).resolve().parent.parent / "README.md"
RESULTS_MD_PATH = Path(__file__).resolve().parent / "RESULTS.md"

RESULTS_START = "<!-- RESULTS:START -->"
RESULTS_END = "<!-- RESULTS:END -->"
MAX_ROWS = 30


def render_summary(history: list[RunResult]) -> str:
    if not history:
        return "No results yet."

    games = len(history)
    wins = [record for record in history if record.won]
    win_rate = round(100 * len(wins) / games)
    avg_attempts = round(sum(record.attempts for record in wins) / len(wins), 2) if wins else None

    streak = 0
    for record in reversed(history):
        if not record.won:
            break
        streak += 1

    return (
        f"**Games:** {games} &nbsp;|&nbsp; **Win rate:** {win_rate}% &nbsp;|&nbsp; "
        f"**Current streak:** {streak} &nbsp;|&nbsp; "
        f"**Avg attempts (wins):** {avg_attempts if avg_attempts is not None else '-'}"
    )


def render_results_table(history: list[RunResult]) -> str:
    lines = [
        "# Results",
        "",
        "> Spoilers: this file lists the solved words.",
        "",
        render_summary(history),
    ]
    if history:
        lines += ["", "| Date | Result | Attempts | Word |", "| --- | --- | --- | --- |"]
        for record in list(reversed(history))[:MAX_ROWS]:
            result = "Won" if record.won else "Lost"
            word = record.solved_word or "-"
            lines.append(f"| {record.date.isoformat()} | {result} | {record.attempts} | {word} |")

    return "\n".join(lines) + "\n"


def update_readme(readme_path: Path = README_PATH, history_path: Path = RESULTS_PATH) -> None:
    history = load_history(history_path)
    section = render_summary(history)

    content = readme_path.read_text(encoding="utf-8")

    before, sep, rest = content.partition(RESULTS_START)
    if not sep:
        raise ValueError(f"{RESULTS_START!r} marker not found in {readme_path}")
    _, sep, after = rest.partition(RESULTS_END)
    if not sep:
        raise ValueError(f"{RESULTS_END!r} marker not found in {readme_path}")

    new_content = f"{before}{RESULTS_START}\n{section}\n{RESULTS_END}{after}"

    readme_path.write_text(new_content, encoding="utf-8")


def update_results_md(path: Path = RESULTS_MD_PATH, history_path: Path = RESULTS_PATH) -> None:
    history = load_history(history_path)
    path.write_text(render_results_table(history), encoding="utf-8")
