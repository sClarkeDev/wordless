import re
from collections.abc import Callable
from contextlib import suppress
from random import uniform
from time import sleep

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from wordle.feedback import FeedbackResult

# A very long array of 5-letter lowercase strings: the game's full word list.
WORD_LIST_PATTERN = re.compile(r'\[(?:"[a-z]{5}",){5000,}"[a-z]{5}"\]')


def _human_pause(low: float = 0.5, high: float = 1.5) -> None:
    sleep(uniform(low, high))


class WebsiteClient:
    WORDLE_URL = "https://www.nytimes.com/games/wordle/index.html?eafs_enabled=false"

    def __init__(self) -> None:
        self._playwright = None
        self._browser = None
        self._page = None
        self._scripts = []

    def open(self, on_status: Callable[[str], None] | None = None) -> None:
        def report(message: str) -> None:
            if on_status:
                on_status(message)

        report("Loading Wordle...")
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(channel="msedge", headless=True)
        self._page = self._browser.new_page()

        # Keep the game's script responses; one of them embeds the word list (see fetch_words).
        self._page.on(
            "response",
            lambda response: (
                self._scripts.append(response)
                if response.request.resource_type == "script" and "/games-assets/" in response.url
                else None
            ),
        )

        self._page.goto(self.WORDLE_URL)

        for button in ("Reject all", "Play", "Continue to Wordle", "Close"):
            self.dismiss_if_present(self._page.get_by_role("button", name=button))

        _human_pause()

    def fetch_words(self) -> list[str]:
        """Read the game's own word list (allowed guesses + answers) out of its JS bundle."""
        for response in self._scripts:
            try:
                body = response.text()
            except PlaywrightError:
                continue
            match = WORD_LIST_PATTERN.search(body)
            if match:
                words = dict.fromkeys(re.findall(r'"([a-z]{5})"', match.group(0)))
                return list(words)
        raise RuntimeError("Could not find the word list in Wordle's scripts")

    def submit_guess(self, word: str, row: int) -> bool:
        """Type and submit a word. Returns False if the game rejected it (row is cleared)."""
        for letter in word:
            self._page.keyboard.press(letter, delay=uniform(20, 60))
            # Short, jittery gap between keystrokes, like fast typing.
            sleep(uniform(0.05, 0.2))

        _human_pause(0.2, 0.5)
        self._page.keyboard.press("Enter")

        # Wait for the animation to finish before returning
        try:
            self._page.wait_for_function(
                """(row) => {
                    const tiles = document.querySelectorAll(`div[aria-label='Row ${row}'] div[role='img']`);
                    const last = tiles[tiles.length - 1];
                    const state = last && last.getAttribute('data-state');
                    const animation = last && last.getAttribute('data-animation');
                    const isRevealed = state && state !== 'tbd' && state !== 'empty' && animation && animation === 'idle';
                    return isRevealed;
                }""",
                arg=row,
                timeout=10000,
            )
        except PlaywrightTimeoutError:
            # A word the game doesn't accept leaves its letters sitting in the row unrevealed.
            last_tile = self._page.locator(f"div[aria-label='Row {row}'] div[role='img']").last
            if last_tile.get_attribute("data-state") != "tbd":
                raise
            for _ in word:
                self._page.keyboard.press("Backspace")
            return False
        return True

    def read_feedback(self, row: int) -> list[FeedbackResult]:
        result = []

        row_locator = self._page.locator(f"div[aria-label='Row {row}']")
        tiles = row_locator.locator("div[role='img']")

        for column in tiles.all():
            state = column.get_attribute("data-state")
            if state == "correct":
                result.append(FeedbackResult.HIT)
            elif state == "present":
                result.append(FeedbackResult.PRESENT)
            elif state == "absent":
                result.append(FeedbackResult.MISS)
            else:
                raise ValueError(f"Unknown tile state: {state}")

        return result

    def close(self) -> None:
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()

    def dismiss_if_present(self, locator, timeout: float = 6000) -> None:
        with suppress(PlaywrightTimeoutError):
            locator.click(timeout=timeout, no_wait_after=True)
