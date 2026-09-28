from storage import append_result

from wordle import run


def main() -> None:
    result = run()
    append_result(result)
    print(result)


if __name__ == "__main__":
    main()
