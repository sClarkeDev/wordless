from collections import Counter

from wordle.feedback import FeedbackResult, Guess


def is_valid_word(candidate: str, history: list[Guess]) -> bool:
    return all(matches_guess(candidate, guess, feedback) for guess, feedback in history)


def matches_guess(candidate: str, guess: str, feedback: list[FeedbackResult]) -> bool:
    for i, guessed_letter in enumerate(guess):
        if feedback[i] == FeedbackResult.HIT and candidate[i] != guessed_letter:
            return False
        if feedback[i] == FeedbackResult.PRESENT and (
            guessed_letter not in candidate or candidate[i] == guessed_letter
        ):
            return False

    # MISS doesn't mean "letter absent" when the same letter is also a HIT/PRESENT
    # elsewhere in the guess - it means "no *more* copies than that". So instead of
    # checking MISS positions individually, work out the required count per letter.
    required_counts = Counter(
        letter
        for letter, result in zip(guess, feedback, strict=True)
        if result in (FeedbackResult.HIT, FeedbackResult.PRESENT)
    )
    missed_letters = {
        letter for letter, result in zip(guess, feedback, strict=True) if result == FeedbackResult.MISS
    }

    for letter in missed_letters:
        min_count = required_counts.get(letter, 0)
        if candidate.count(letter) != min_count:
            return False

    return all(candidate.count(letter) >= min_count for letter, min_count in required_counts.items())


def choose_guess(words: list[str], history: list[Guess], tried_words: set[str]) -> str | None:
    remaining = [word for word in words if word not in tried_words and is_valid_word(word, history)]
    if not remaining:
        return None

    # Score candidates by how common their (distinct) letters are across the
    # remaining pool - using set(word) rather than raw letters means repeated
    # letters don't inflate a word's own score, so words that test 5 different
    # letters naturally score higher than words that repeat a letter.
    letter_frequencies = Counter(letter for word in remaining for letter in set(word))

    def score(word: str) -> int:
        return sum(letter_frequencies[letter] for letter in set(word))

    return max(remaining, key=score)
