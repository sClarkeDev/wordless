# Wordless Web

The [live results page](https://wordless.sclarke.dev/) for Wordless. It shows today's solve, overall stats (games played, win rate, streak, average guesses) and the full history of daily runs. Built with React, TypeScript and Vite, and deployed to GitHub Pages.

## How it works

The site has no backend. At runtime it fetches [data/results.json](../data/results.json) straight from the `main` branch on GitHub, so new daily results appear without redeploying the site.

During `npm run dev`, the Vite server serves your local `data/results.json` instead, so you can preview changes to the data before they are pushed. Set `VITE_RESULTS_URL` to load results from any other URL.

## Getting started

Requires [Node.js](https://nodejs.org/) 22 or newer.

```sh
cd web
npm install
npm run dev
```

## Scripts

| Command           | Description                                     |
| ----------------- | ----------------------------------------------- |
| `npm run dev`     | Start the dev server with hot reload            |
| `npm run build`   | Type-check and build the site into `dist/`      |
| `npm run preview` | Serve the production build locally              |
| `npm run lint`    | Lint with ESLint (`lint:fix` to auto-fix)       |
| `npm run format`  | Format with Prettier (`format:check` to verify) |

## Deployment

The [Deploy web](../.github/workflows/pages.yml) workflow builds and publishes the site to GitHub Pages on every push to `main` that touches `web/`. It can also be run manually from the Actions tab.
