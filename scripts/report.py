from pathlib import Path

from storage import DATA_DIR, RESULTS_PATH, load_history

from wordle.result import RunResult

RESULTS_MD_PATH = DATA_DIR / "RESULTS.md"

MAX_ROWS = 30


def render_summary(history: list[RunResult]) -> str:
    if not history:
        return "No results yet."

    games = len(history)
    wins = [record for record in history if record.won]
    win_rate = round(100 * len(wins) / games)
    avg_attempts = f"{sum(record.attempts for record in wins) / len(wins):.1f}" if wins else "-"

    streak = 0
    for record in reversed(history):
        if not record.won:
            break
        streak += 1

    return "\n".join(
        [
            "| Games | Win rate | Current streak | Avg. attempts (wins) |",
            "| ---: | ---: | ---: | ---: |",
            f"| {games} | {win_rate}% | {streak} | {avg_attempts} |",
        ]
    )


def render_results_table(history: list[RunResult]) -> str:
    lines = [
        "# Results",
        "",
        "### Summary",
        "",
        render_summary(history),
    ]
    if history:
        lines += ["", "### History", "", "| Date | Result | Attempts | Word |", "| --- | --- | --- | --- |"]
        for record in list(reversed(history))[:MAX_ROWS]:
            result = "Won" if record.won else "Lost"
            word = record.solved_word or "-"
            lines.append(f"| {record.date.isoformat()} | {result} | {record.attempts} | {word} |")

    return "\n".join(lines) + "\n"


def update_results_md(path: Path = RESULTS_MD_PATH, history_path: Path = RESULTS_PATH) -> None:
    history = load_history(history_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(render_results_table(history), encoding="utf-8")
