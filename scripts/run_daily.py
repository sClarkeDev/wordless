import argparse
import logging

from readme import update_readme
from storage import append_result

from wordle import run


def main() -> None:
    args = parse_args()
    logging.basicConfig(
        level=logging.DEBUG if args.headless else logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )
    logging.getLogger("wordle").setLevel(logging.DEBUG)
    result = run(headless=args.headless)
    append_result(result)
    update_readme()
    print(result)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Solve today's Wordle automatically.")
    parser.add_argument(
        "--headless",
        action="store_true",
        help="Run the browser headless (used in CI).",
    )
    return parser.parse_args()


if __name__ == "__main__":
    main()
