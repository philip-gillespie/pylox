import argparse
import sys
from dataclasses import dataclass, replace


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


@dataclass(frozen=True)
class LoxState:
    had_error: bool = False


def run_repl() -> None:
    state = LoxState()
    while True:
        try:
            line = input("> ")
        except EOFError:
            break
        if line == "":
            continue
        state = run(line, state)
        if state.had_error:
            state = replace(state, had_error=False)


def run_script(filename: str) -> None:
    state = LoxState()
    with open(filename) as f:
        text = f.read()
    state = run(text, state)
    if state.had_error:
        sys.exit(65)


def run(text: str, state: LoxState) -> LoxState:
    print(text)
    return state


def handle_lox_error(line: int, where: str, message: str, state: LoxState) -> LoxState:
    sys.stderr.write(f"[line {line}] Error {where}:{message}\n")
    return replace(state, had_error=True)


if __name__ == "__main__":
    main()
