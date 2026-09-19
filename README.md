# Wordle Solver

Automatically solves the daily [NYT Wordle](https://www.nytimes.com/games/wordle/index.html) by driving the real site with Playwright, picking each guess to maximize letter coverage across the remaining candidate words.

Runs once a day via GitHub Actions against the live puzzle; results below are updated automatically.

## Usage

```
uv run wordle
uv run wordle --headless  # headless
```

`scripts/run_daily.py` is a thin wrapper around this used by the GitHub Actions workflow to also record results to `scripts/results.json` and update the README stats below — not needed for normal use.

## Results

<!-- RESULTS:START -->
**Games:** 1 &nbsp;|&nbsp; **Win rate:** 100% &nbsp;|&nbsp; **Current streak:** 1 &nbsp;|&nbsp; **Avg attempts (wins):** 5.0

<details>
<summary>Show results table (spoilers)</summary>

| Date | Result | Attempts | Word |
| --- | --- | --- | --- |
| 2026-09-19 | Won | 5 | waken |

</details>
<!-- RESULTS:END -->
