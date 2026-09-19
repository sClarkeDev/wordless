import logging
import re
from collections.abc import Callable
from contextlib import suppress
from random import uniform
from time import sleep

from playwright.sync_api import Error as PlaywrightError
from playwright.sync_api import TimeoutError as PlaywrightTimeoutError
from playwright.sync_api import sync_playwright

from wordle.feedback import FeedbackResult

log = logging.getLogger(__name__)

# A very long array of 5-letter lowercase strings: the game's full word list.
WORD_LIST_PATTERN = re.compile(r'\[(?:"[a-z]{5}",){5000,}"[a-z]{5}"\]')


def _human_pause(low: float = 0.5, high: float = 1.5) -> None:
    sleep(uniform(low, high))


class WebsiteClient:
    WORDLE_URL = "https://www.nytimes.com/games/wordle/index.html?eafs_enabled=false"

    def __init__(self, headless: bool = False) -> None:
        self._headless = headless
        self._playwright = None
        self._browser = None
        self._page = None
        self._scripts = []

    def open(self, on_status: Callable[[str], None] | None = None) -> None:
        def report(message: str) -> None:
            if on_status:
                on_status(message)

        report("Launching browser...")
        log.info("Launching firefox (headless=%s)", self._headless)
        self._playwright = sync_playwright().start()
        self._browser = self._playwright.firefox.launch(headless=self._headless)
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

        self._page.on("console", lambda msg: log.debug("browser console [%s]: %s", msg.type, msg.text))
        self._page.on("pageerror", lambda err: log.warning("browser page error: %s", err))

        report("Loading Wordle...")
        log.info("Navigating to %s", self.WORDLE_URL)
        self._page.goto(self.WORDLE_URL)
        log.info("Loaded: url=%s title=%r", self._page.url, self._page.title())

        report("Dismissing popups...")
        for button in ("Reject all", "Play", "Continue to Wordle"):
            self.dismiss_if_present(self._page.get_by_role("button", name=button))
        self._close_modals()

        _human_pause()
        log.info("After popups: %s", self._describe_board())

    def _close_modals(self, first_wait: float = 15000, max_rounds: int = 4) -> None:
        """Close the game's modal(s) (e.g. how-to-play) and verify they are really gone.

        The modal can render well after the previous popup is dismissed, especially on a slow CI
        runner, so wait generously for the first one and re-check after each click.
        """
        close = self._page.locator("button[aria-label='Close']").first
        for round_ in range(1, max_rounds + 1):
            try:
                close.wait_for(state="visible", timeout=first_wait if round_ == 1 else 3000)
            except PlaywrightTimeoutError:
                log.info("No visible Close button (round %d); modals done", round_)
                return
            log.info("Close button visible (round %d); clicking", round_)
            try:
                close.click(timeout=5000)
                close.wait_for(state="hidden", timeout=5000)
            except PlaywrightTimeoutError:
                log.warning("Close click did not hide the modal; pressing Escape")
                self._page.keyboard.press("Escape")
        log.warning("Modal still present after %d rounds", max_rounds)

    def fetch_words(self) -> list[str]:
        """Read the game's own word list (allowed guesses + answers) out of its JS bundle."""
        log.debug("Scanning %d captured game scripts for the word list", len(self._scripts))
        for response in self._scripts:
            try:
                body = response.text()
            except PlaywrightError:
                log.debug("Could not read body of %s", response.url)
                continue
            match = WORD_LIST_PATTERN.search(body)
            if match:
                words = dict.fromkeys(re.findall(r'"([a-z]{5})"', match.group(0)))
                return list(words)
        raise RuntimeError("Could not find the word list in Wordle's scripts")

    def submit_guess(self, word: str, row: int) -> bool:
        """Type and submit a word. Returns False if the game rejected it (row is cleared)."""
        log.debug("Typing %s into row %d; board before: %s", word, row, self._describe_board())
        for letter in word:
            self._page.keyboard.press(letter, delay=uniform(20, 60))
            # Short, jittery gap between keystrokes, like fast typing.
            sleep(uniform(0.05, 0.2))

        _human_pause(0.2, 0.5)
        log.debug("Typed; board before Enter: %s", self._describe_board())
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
            log.error("Timed out revealing %s in row %d: %s", word, row, self._describe_board())
            self._dump_diagnostics()
            # A word the game doesn't accept leaves its letters sitting in the row unrevealed.
            last_tile = self._page.locator(f"div[aria-label='Row {row}'] div[role='img']").last
            if last_tile.get_attribute("data-state") != "tbd":
                raise
            for _ in word:
                self._page.keyboard.press("Backspace")
            return False
        log.debug("Row %d revealed: %s", row, self._describe_board())
        return True

    def _describe_board(self) -> str:
        """One-line snapshot of every tile: letter/state/animation, plus toasts and open dialogs."""
        try:
            return self._page.evaluate(
                """() => {
                    const rows = [...document.querySelectorAll("div[aria-label^='Row ']")].map(r =>
                        [...r.querySelectorAll("div[role='img']")]
                            .map(t => `${(t.textContent || '_').trim() || '_'}:${t.dataset.state}:${t.dataset.animation}`)
                            .join(' '));
                    const toasts = [...document.querySelectorAll("[class*='Toast'], [role='alert']")]
                        .map(e => e.textContent.trim()).filter(Boolean);
                    const dialogs = [...document.querySelectorAll("[role='dialog'], dialog[open]")]
                        .map(e => e.getAttribute('aria-label') || e.id || e.className);
                    const focus = document.activeElement && document.activeElement.tagName;
                    return JSON.stringify({rows, toasts, dialogs, focus});
                }"""
            )
        except PlaywrightError as error:
            return f"<could not read board: {error}>"

    def _dump_diagnostics(self) -> None:
        with suppress(PlaywrightError):
            self._page.screenshot(path="wordle-timeout.png", full_page=True)
            log.error("Saved screenshot to wordle-timeout.png (url=%s)", self._page.url)
        with suppress(PlaywrightError):
            with open("wordle-timeout.html", "w") as f:
                f.write(self._page.content())
            log.error("Saved page HTML to wordle-timeout.html")

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

    def dismiss_if_present(self, locator, timeout: float = 4000) -> None:
        try:
            locator.click(timeout=timeout, no_wait_after=True)
            log.info("Clicked %s", locator)
        except PlaywrightTimeoutError:
            log.debug("Not present: %s", locator)
