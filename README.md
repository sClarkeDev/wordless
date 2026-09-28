# Wordless

[![Daily solve](https://github.com/sClarkeDev/wordless/actions/workflows/daily.yml/badge.svg)](https://github.com/sClarkeDev/wordless/actions/workflows/daily.yml)
[![Deploy web](https://github.com/sClarkeDev/wordless/actions/workflows/pages.yml/badge.svg)](https://github.com/sClarkeDev/wordless/actions/workflows/pages.yml)
[![Latest release](https://img.shields.io/github/v/release/sClarkeDev/wordless)](../../releases/latest)

An automated solver for the daily [NYT Wordle](https://www.nytimes.com/games/wordle/index.html). It plays the real game in a browser, and a companion web app tracks every daily result.

**[View live results →](https://wordless.sclarke.dev/)**

## Overview

| Component | Stack | Description |
| --- | --- | --- |
| Solver ([`src/wordle`](src/wordle)) | Python 3.14, Playwright, Rich | Opens Wordle in Microsoft Edge, plays guesses through the page and reads the tile feedback. |
| Results site ([`web`](web)) | React 19, TypeScript, Vite | Dashboard showing today's solve, win rate, streak, average guesses and full history. |
| Automation ([`.github/workflows`](.github/workflows)) | GitHub Actions, GitHub Pages | Solves the puzzle daily, deploys the site and publishes a Windows build. |

## How the solver works

1. **Word list**: rather than bundling a dictionary, it extracts the game's own list of valid words from Wordle's JavaScript bundle at runtime, so it always matches what the game accepts.
2. **Filtering**: after each guess, candidates are narrowed using the hit / present / miss feedback. Repeated letters are handled correctly: a "miss" on a letter that is also a hit elsewhere caps its count instead of excluding it.
3. **Guess selection**: each remaining candidate is scored by how common its *distinct* letters are across the remaining pool, favouring words that test five different high-value letters.
4. **Playing**: guesses are typed into the live page with human-like pauses; any word the game rejects is cleared and skipped.

The core logic is in [`solver.py`](src/wordle/solver.py) and the browser automation in [`client.py`](src/wordle/client.py).

## Automation

| Workflow | Trigger | What it does |
| --- | --- | --- |
| [Daily Wordle](.github/workflows/daily.yml) | Every day at 00:05 UTC | Solves the live puzzle and commits the outcome to [`data/results.json`](data/results.json). |
| [Deploy web](.github/workflows/pages.yml) | Push to `web/` | Builds the site and deploys it to GitHub Pages. |
| [Release](.github/workflows/release.yml) | Push to solver source | Builds a standalone Windows `.exe` with PyInstaller, smoke-tests it and publishes a versioned release with a SHA-256 checksum. |

The site has no backend: it fetches `results.json` from the repository at runtime, so new results appear without a redeploy.

## Running it locally

### Windows executable

Download the latest `.exe` from [Releases](../../releases/latest) and run it.

### From source

Requires [uv](https://docs.astral.sh/uv/) (it installs the correct Python version automatically).

```sh
git clone https://github.com/sClarkeDev/wordless.git
cd wordless
uv sync
uv run playwright install msedge  # not needed on Windows
uv run wordle
```

### Results site

See [`web/README.md`](web/README.md) for development instructions.

## Disclaimer

Wordless is an independent, unofficial project for personal and educational use. It is not affiliated with, endorsed by, or sponsored by The New York Times Company.
