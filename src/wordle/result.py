from dataclasses import dataclass
from datetime import date

from wordle.feedback import FeedbackResult, Guess

EMOJI = {
    FeedbackResult.HIT: "🟩",
    FeedbackResult.PRESENT: "🟨",
    FeedbackResult.MISS: "⬛",
}


def format_guess(word: str, feedback: list[FeedbackResult]) -> str:
    return f"{word.upper()}  {''.join(EMOJI[f] for f in feedback)}"


def _attempts(count: int) -> str:
    return f"{count} attempt" if count == 1 else f"{count} attempts"


@dataclass
class RunResult:
    date: date
    won: bool
    attempts: int
    guesses: list[Guess]
    solved_word: str | None = None

    def to_dict(self) -> dict:
        return {
            "date": self.date.isoformat(),
            "won": self.won,
            "attempts": self.attempts,
            "solved_word": self.solved_word,
            "guesses": [[word, [f.value for f in feedback]] for word, feedback in self.guesses],
        }

    @classmethod
    def from_dict(cls, data: dict) -> RunResult:
        return cls(
            date=date.fromisoformat(data["date"]),
            won=data["won"],
            attempts=data["attempts"],
            guesses=[(word, [FeedbackResult(value) for value in values]) for word, values in data["guesses"]],
            solved_word=data["solved_word"],
        )

    def summary(self) -> str:
        attempts = _attempts(self.attempts)
        lines = [f"Won in {attempts}" if self.won else f"Lost after {attempts}"]
        for i, (word, feedback) in enumerate(self.guesses, start=1):
            lines.append(f"{i}. {format_guess(word, feedback)}")
        if self.solved_word:
            lines.append(f"Word: {self.solved_word}")
        return "\n".join(lines)

    __str__ = summary
