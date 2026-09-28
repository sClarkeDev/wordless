export type Feedback = 'hit' | 'present' | 'miss'

export type Guess = [word: string, feedback: Feedback[]]

export interface RunResult {
  date: string
  won: boolean
  attempts: number
  solved_word: string | null
  guesses: Guess[]
}

export interface Stats {
  games: number
  winRate: number
  streak: number
  avgAttempts: number | null
}

export const MAX_ATTEMPTS = 6

const REMOTE_URL = `https://raw.githubusercontent.com/${import.meta.env.VITE_REPO}/main/data/results.json`

// In dev, the Vite server serves the local data/results.json at /results.json.
const RESULTS_URL: string =
  import.meta.env.VITE_RESULTS_URL ?? (import.meta.env.DEV ? '/results.json' : REMOTE_URL)

// Returns results newest first.
export async function loadResults(signal?: AbortSignal): Promise<RunResult[]> {
  const response = await fetch(RESULTS_URL, { cache: 'no-cache', signal })
  if (!response.ok) {
    throw new Error(`Failed to load results (${response.status})`)
  }
  const results = (await response.json()) as RunResult[]
  return [...results].sort((a, b) => b.date.localeCompare(a.date))
}

// Expects results newest first; the streak counts consecutive wins back from the latest.
export function computeStats(results: RunResult[]): Stats {
  const wins = results.filter((result) => result.won)
  const streak = results.findIndex((result) => !result.won)
  return {
    games: results.length,
    winRate: results.length ? Math.round((100 * wins.length) / results.length) : 0,
    streak: streak === -1 ? results.length : streak,
    avgAttempts: wins.length
      ? wins.reduce((sum, result) => sum + result.attempts, 0) / wins.length
      : null,
  }
}

function parseDate(iso: string): Date {
  const [year, month, day] = iso.split('-').map(Number)
  return new Date(year, month - 1, day)
}

export function isToday(iso: string): boolean {
  return parseDate(iso).toDateString() === new Date().toDateString()
}

export function formatDate(iso: string, options: Intl.DateTimeFormatOptions): string {
  return parseDate(iso).toLocaleDateString(undefined, options)
}
