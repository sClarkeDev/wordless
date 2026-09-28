import { useEffect, useState } from 'react'
import { Grid, ResultBadge } from './components/Grid.tsx'
import { HistoryTable } from './components/HistoryTable.tsx'
import { ResultDialog } from './components/ResultDialog.tsx'
import { computeStats, formatDate, isToday, loadResults, type RunResult } from './data.ts'

const REPO_URL = `https://github.com/${import.meta.env.VITE_REPO}`

type State =
  | { status: 'loading' }
  | { status: 'error'; message: string }
  | { status: 'ready'; results: RunResult[] }

function App() {
  const [state, setState] = useState<State>({ status: 'loading' })

  useEffect(() => {
    const controller = new AbortController()
    loadResults(controller.signal)
      .then((results) => setState({ status: 'ready', results }))
      .catch((error: unknown) => {
        if (controller.signal.aborted) return
        setState({
          status: 'error',
          message: error instanceof Error ? error.message : String(error),
        })
      })
    return () => controller.abort()
  }, [])

  return (
    <main>
      <header>
        <div className="title-row">
          <h1>Wordless</h1>
          <a className="icon-link" href={REPO_URL} aria-label="View source on GitHub">
            <svg viewBox="0 0 16 16" width="22" height="22" aria-hidden="true">
              <path
                fill="currentColor"
                d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"
              />
            </svg>
          </a>
        </div>
        <p className="muted">Daily NYT Wordle, solved automatically.</p>
      </header>

      {state.status === 'loading' && <p className="muted">Loading results…</p>}
      {state.status === 'error' && <p className="error">{state.message}</p>}
      {state.status === 'ready' && <Results results={state.results} />}

      <footer className="muted">
        <p>
          Wordless is an independent, unofficial project. It is not affiliated with, endorsed by, or
          sponsored by The New York Times Company.
        </p>
      </footer>
    </main>
  )
}

function Results({ results }: { results: RunResult[] }) {
  const [selected, setSelected] = useState<RunResult | null>(null)

  if (results.length === 0) {
    return <p className="muted">No results yet.</p>
  }

  const [latest] = results
  const stats = computeStats(results)

  return (
    <>
      <section className="card today">
        <div className="today-head">
          <span className="eyebrow">
            {isToday(latest.date)
              ? 'Today'
              : formatDate(latest.date, { weekday: 'long', month: 'long', day: 'numeric' })}
          </span>
          <ResultBadge result={latest} />
        </div>
        <Grid guesses={latest.guesses} />
        {latest.solved_word && <p className="answer">{latest.solved_word}</p>}
      </section>

      <dl className="stats">
        <Stat label="Played" value={stats.games} />
        <Stat label="Win %" value={stats.winRate} />
        <Stat label="Streak" value={stats.streak} />
        <Stat label="Avg." value={stats.avgAttempts?.toFixed(1) ?? '—'} />
      </dl>

      <section>
        <h2>History</h2>
        <HistoryTable results={results} onSelect={setSelected} />
        <ResultDialog result={selected} onClose={() => setSelected(null)} />
      </section>
    </>
  )
}

function Stat({ label, value }: { label: string; value: string | number }) {
  return (
    <div>
      <dt>{label}</dt>
      <dd>{value}</dd>
    </div>
  )
}

export default App
