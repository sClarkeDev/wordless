import { useEffect, useRef } from 'react'
import { formatDate, type RunResult } from '../data.ts'
import { Grid, ResultBadge } from './Grid.tsx'

interface Props {
  result: RunResult | null
  onClose: () => void
}

export function ResultDialog({ result, onClose }: Props) {
  const dialogRef = useRef<HTMLDialogElement>(null)

  useEffect(() => {
    const dialog = dialogRef.current
    if (result && dialog && !dialog.open) {
      dialog.showModal()
    }
  }, [result])

  return (
    <dialog
      ref={dialogRef}
      onClose={onClose}
      // The body fills the dialog, so a click landing on the dialog itself is on the backdrop.
      onClick={(event) => event.target === dialogRef.current && dialogRef.current.close()}
    >
      {result && (
        <div className="dialog-body">
          <div className="today-head">
            <span className="eyebrow">
              {formatDate(result.date, { weekday: 'long', month: 'long', day: 'numeric' })}
            </span>
            <ResultBadge result={result} />
          </div>
          <Grid guesses={result.guesses} />
          {result.solved_word && <p className="answer">{result.solved_word}</p>}
          <button type="button" className="close" onClick={() => dialogRef.current?.close()}>
            Close
          </button>
        </div>
      )}
    </dialog>
  )
}
