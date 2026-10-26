"""Edit distance and spelling suggestions."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

WORDS_PATH = Path(__file__).with_name("words.txt")


def edit_distance(word1: str, word2: str, max_distance: int | None = None) -> int:
    """Return the Levenshtein distance between two strings.

    Uses the Wagner-Fischer dynamic programming algorithm, keeping only two
    rows of the table. When max_distance is given, the computation stops as
    soon as the distance is known to exceed it, and max_distance + 1 is
    returned instead of the exact value.
    """
    if max_distance is not None and abs(len(word1) - len(word2)) > max_distance:
        return max_distance + 1

    # Iterate over the longer word so each row is as short as possible.
    if len(word1) < len(word2):
        word1, word2 = word2, word1

    previous = list(range(len(word2) + 1))
    for i, char1 in enumerate(word1, start=1):
        current = [i]
        for j, char2 in enumerate(word2, start=1):
            substitute = previous[j - 1] + (char1 != char2)
            insert = current[j - 1] + 1
            delete = previous[j] + 1
            current.append(min(substitute, insert, delete))
        # Every path to the last cell passes through this row, so once its
        # smallest value is over the limit the final distance is too.
        if max_distance is not None and min(current) > max_distance:
            return max_distance + 1
        previous = current

    distance = previous[-1]
    if max_distance is not None and distance > max_distance:
        return max_distance + 1
    return distance


def load_words(path: Path | None = None) -> list[str]:
    """Read a word list with one word per line, most frequent first.

    Defaults to the bundled list of common English words. Words are
    lowercased, blank lines are skipped and duplicates keep their first
    (most frequent) position.
    """
    text = Path(path or WORDS_PATH).read_text(encoding="utf-8")
    words = (line.strip().lower() for line in text.splitlines())
    return list(dict.fromkeys(word for word in words if word))


def suggest(
    word: str,
    words: Iterable[str],
    max_distance: int = 2,
    limit: int = 5,
) -> list[str]:
    """Suggest corrections for word from words, best first.

    Candidates within max_distance edits are ranked by edit distance, then by
    their position in words, so a frequency-ordered list puts common words
    first. A word that is already in the list returns only itself.
    """
    word = word.strip().lower()
    words = list(words)
    if word in words:
        return [word]

    scored = []
    for rank, candidate in enumerate(words):
        distance = edit_distance(word, candidate, max_distance)
        if distance <= max_distance:
            scored.append((distance, rank, candidate))
    scored.sort()
    return [candidate for _, _, candidate in scored[:limit]]
