from report import update_results_md
from storage import append_result

from wordle import run


def main() -> None:
    result = run()
    append_result(result)
    update_results_md()
    print(result)


if __name__ == "__main__":
    main()
