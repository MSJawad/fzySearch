"""Command line interface: python -m fzysearch WORD [WORD ...]"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence
from pathlib import Path

from .core import load_words, suggest


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="fzysearch",
        description="Suggest spelling corrections using edit distance.",
    )
    parser.add_argument(
        "words",
        nargs="*",
        metavar="WORD",
        help="words to check (read from standard input when omitted)",
    )
    parser.add_argument(
        "-d",
        "--max-distance",
        type=int,
        default=2,
        help="largest edit distance to suggest (default: 2)",
    )
    parser.add_argument(
        "-n",
        "--limit",
        type=int,
        default=5,
        help="most suggestions to show per word (default: 5)",
    )
    parser.add_argument(
        "-w",
        "--words-file",
        type=Path,
        help="word list to use, one word per line, most frequent first",
    )
    args = parser.parse_args(argv)
    if args.max_distance < 0:
        parser.error("--max-distance must be 0 or more")
    if args.limit < 1:
        parser.error("--limit must be 1 or more")

    try:
        dictionary = load_words(args.words_file)
    except OSError as error:
        parser.error(f"cannot read word list: {error}")

    queries = [query.strip() for query in args.words or sys.stdin.read().split()]
    for query in filter(None, queries):
        suggestions = suggest(query, dictionary, args.max_distance, args.limit)
        if suggestions == [query.lower()]:
            print(f"{query}: correct")
        elif suggestions:
            print(f"{query}: {', '.join(suggestions)}")
        else:
            print(f"{query}: no suggestions")
    return 0


if __name__ == "__main__":
    sys.exit(main())
