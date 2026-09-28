import { MAX_ATTEMPTS, type Guess, type RunResult } from '../data.ts'

const LABELS = { hit: 'correct', present: 'present', miss: 'absent' } as const

export function Grid({ guesses }: { guesses: Guess[] }) {
  const rows = Array.from({ length: Math.max(MAX_ATTEMPTS, guesses.length) }, (_, i) => guesses[i])

  return (
    <div className="grid" role="img" aria-label={`${guesses.length} guesses`}>
      {rows.map((guess, row) => (
        <div className="grid-row" key={row}>
          {Array.from({ length: 5 }, (_, col) => {
            const feedback = guess?.[1][col]
            const letter = guess?.[0][col] ?? ''
            return (
              <div
                className={`tile ${feedback ?? 'empty'}`}
                key={col}
                title={feedback ? `${letter.toUpperCase()} ${LABELS[feedback]}` : undefined}
              >
                {letter}
              </div>
            )
          })}
        </div>
      ))}
    </div>
  )
}

export function ResultBadge({ result }: { result: RunResult }) {
  return (
    <span className={`badge ${result.won ? 'won' : 'lost'}`}>
      {result.won ? `Solved in ${result.attempts}/${MAX_ATTEMPTS}` : 'Missed'}
    </span>
  )
}
