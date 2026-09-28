import { formatDate, MAX_ATTEMPTS, type RunResult } from '../data.ts'

interface Props {
  results: RunResult[]
  onSelect: (result: RunResult) => void
}

export function HistoryTable({ results, onSelect }: Props) {
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Date</th>
            <th>Word</th>
            <th className="num">Score</th>
          </tr>
        </thead>
        <tbody>
          {results.map((result) => (
            <tr
              key={result.date}
              className="clickable"
              tabIndex={0}
              onClick={() => onSelect(result)}
              onKeyDown={(event) => {
                if (event.key === 'Enter' || event.key === ' ') {
                  event.preventDefault()
                  onSelect(result)
                }
              }}
            >
              <td className="date">
                {formatDate(result.date, { month: 'short', day: 'numeric', year: 'numeric' })}
              </td>
              <td className="word">{result.solved_word ?? '—'}</td>
              <td className="num">
                <span className={`badge ${result.won ? 'won' : 'lost'}`}>
                  {result.won ? result.attempts : 'X'}/{MAX_ATTEMPTS}
                </span>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
