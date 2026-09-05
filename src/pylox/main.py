import argparse


def main() -> None:
    filename = parse_args()
    if filename is None:
        run_repl()
    else:
        run_script(filename)


def parse_args() -> str | None:
    parser = argparse.ArgumentParser(
        prog="pylox",
        description="pylox — an interpreter for the Lox programming language, "
        "implemented in Python.",
        epilog=(
            "If no script is given, pylox starts an interactive REPL. "
            "Otherwise, it executes the given .lox file and exits.\n\n"
            "Examples:\n"
            "  pylox                  Start the REPL\n"
            "  pylox script.lox       Run a Lox script\n\n"
            "Based on the Lox language from 'Crafting Interpreters' by Robert Nystrom."
        ),
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )

    parser.add_argument("filename", nargs="?", default=None, type=str)
    args: argparse.Namespace = parser.parse_args()
    return args.filename


def run_repl() -> None:
    raise NotImplementedError


def run_script(filename: str) -> None:
    raise NotImplementedError


if __name__ == "__main__":
    main()
