import json
import os
from pathlib import Path

from wordle.result import RunResult

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
RESULTS_PATH = DATA_DIR / "results.json"


def load_history(path: Path = RESULTS_PATH) -> list[RunResult]:
    if not path.exists():
        return []
    return [RunResult.from_dict(record) for record in json.loads(path.read_text(encoding="utf-8"))]


def append_result(result: RunResult, path: Path = RESULTS_PATH) -> None:
    history = [record for record in load_history(path) if record.date != result.date]
    history.append(result)
    history.sort(key=lambda record: record.date)

    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps([record.to_dict() for record in history], indent=2) + "\n"

    # Write to a temp file first so a crash mid-write can't corrupt the committed record.
    tmp_path = path.with_name(path.name + ".tmp")
    tmp_path.write_text(payload, encoding="utf-8")
    os.replace(tmp_path, path)
