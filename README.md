# Wordle Solver

Automatically solves the daily [NYT Wordle](https://www.nytimes.com/games/wordle/index.html) by driving the real site with Playwright, picking each guess to maximize letter coverage across the remaining candidate words. A GitHub Actions workflow runs it against the live puzzle every day.

## Getting started

Choose one of the two options below.

### Option 1: Windows executable

1. Download the latest `.exe` from the [Releases page](../../releases/latest).
2. Double-click it to run.

### Option 2: Run from source (any platform)

Requires [uv](https://docs.astral.sh/uv/), which installs the correct Python version automatically.

```sh
git clone https://github.com/sClarkeDev/wordless.git
cd wordless
uv sync
uv run playwright install msedge  # skip on Windows, Edge is already installed
uv run wordle
```

## Results

Daily results are recorded in [RESULTS.md](data/RESULTS.md).
