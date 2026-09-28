import { readFile } from 'node:fs/promises'
import { fileURLToPath } from 'node:url'
import react from '@vitejs/plugin-react'
import { defineConfig, type Plugin } from 'vite'

// GitHub Actions sets GITHUB_REPOSITORY (owner/name); the fallback covers local builds.
const REPO = process.env.GITHUB_REPOSITORY ?? 'sClarkeDev/wordless'

const RESULTS_PATH = fileURLToPath(new URL('../data/results.json', import.meta.url))

// Serves the repo's local data/results.json at /results.json during `vite dev`.
function localResults(): Plugin {
  return {
    name: 'local-results',
    apply: 'serve',
    configureServer(server) {
      server.middlewares.use('/results.json', async (_req, res) => {
        try {
          res.setHeader('Content-Type', 'application/json')
          res.end(await readFile(RESULTS_PATH))
        } catch {
          res.statusCode = 404
          res.end('[]')
        }
      })
    },
  }
}

// https://vite.dev/config/
export default defineConfig({
  // Served from the root of the custom domain (wordless.sclarke.dev).
  base: '/',
  define: {
    'import.meta.env.VITE_REPO': JSON.stringify(REPO),
  },
  plugins: [react(), localResults()],
})
