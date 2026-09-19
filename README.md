# Wordle Solver

Automatically solves the daily [NYT Wordle](https://www.nytimes.com/games/wordle/index.html) by driving the real site with Playwright, picking each guess to maximize letter coverage across the remaining candidate words.

Runs once a day via GitHub Actions against the live puzzle; results below are updated automatically.

## Download (Windows)

Grab the latest `wordle-<version>-windows-x64.exe` from the [Releases page](../../releases/latest) and run it. It drives Microsoft Edge (preinstalled on Windows 10/11), so there is nothing else to install.

Releases are built automatically on every push to `main` that changes the app. Versions are `MAJOR.MINOR.BUILD`: bump `MAJOR.MINOR` in `pyproject.toml` by hand for meaningful changes; `BUILD` is the CI run number.

## Usage

```
uv run wordle
uv run wordle --headless  # headless
```

`scripts/run_daily.py` is a thin wrapper around this used by the GitHub Actions workflow to also record results to `scripts/results.json`, update the README stats below, and write the full per-day table to `scripts/RESULTS.md` — not needed for normal use.

## Results

<!-- RESULTS:START -->
**Games:** 1 &nbsp;|&nbsp; **Win rate:** 100% &nbsp;|&nbsp; **Current streak:** 1 &nbsp;|&nbsp; **Avg attempts (wins):** 5.0
<!-- RESULTS:END -->

[scripts/RESULTS.md](scripts/RESULTS.md) (spoilers).
