from enum import Enum


class FeedbackResult(Enum):
    HIT = "hit"  # correct letter, correct spot
    PRESENT = "present"  # letter in word, wrong spot
    MISS = "miss"  # letter not in word


Guess = tuple[str, list[FeedbackResult]]
