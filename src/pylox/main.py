"""
main.py
"""

import argparse


from pylox.lox import Lox


def main():
    parser = argparse.ArgumentParser(prog="pylox")
    parser.add_argument("filename", nargs="?")  # Optional argument for filename
    args = parser.parse_args()
    lox = Lox()
    if args.filename is not None:
        lox.run_file(args.filename)
    else:
        lox.run_prompt()


if __name__ == "__main__":
    main()
