import io
import random

import pytest

from fzysearch import WORDS_PATH, edit_distance, load_words, suggest
from fzysearch.__main__ import main


@pytest.fixture(scope="module")
def words():
    return load_words()


def reference_distance(a, b):
    """Full-table Levenshtein distance, used to check the optimised version."""
    table = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        table[i][0] = i
    for j in range(len(b) + 1):
        table[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            table[i][j] = min(
                table[i - 1][j] + 1,
                table[i][j - 1] + 1,
                table[i - 1][j - 1] + (a[i - 1] != b[j - 1]),
            )
    return table[-1][-1]


@pytest.mark.parametrize(
    "a, b, expected",
    [
        ("", "", 0),
        ("", "abc", 3),
        ("abc", "", 3),
        ("same", "same", 0),
        ("kitten", "sitting", 3),
        ("flaw", "lawn", 2),
        ("saturday", "sunday", 3),
        ("recieve", "receive", 2),
        ("a", "b", 1),
    ],
)
def test_edit_distance(a, b, expected):
    assert edit_distance(a, b) == expected
    assert edit_distance(b, a) == expected


def test_edit_distance_matches_reference():
    rng = random.Random(0)
    for _ in range(1000):
        a = "".join(rng.choice("abc") for _ in range(rng.randint(0, 8)))
        b = "".join(rng.choice("abc") for _ in range(rng.randint(0, 8)))
        expected = reference_distance(a, b)
        assert edit_distance(a, b) == expected
        for limit in range(4):
            assert edit_distance(a, b, limit) == min(expected, limit + 1)


def test_edit_distance_bound_skips_long_words():
    assert edit_distance("a", "abcdefgh", max_distance=2) == 3


def test_load_words_is_frequency_ordered_and_unique(words):
    assert WORDS_PATH.is_file()
    assert words[:5] == ["the", "of", "and", "to", "a"]
    assert len(words) == len(set(words))
    assert "" not in words


def test_load_words_custom_file(tmp_path):
    path = tmp_path / "list.txt"
    path.write_text("Zeta\n\nalpha\nzeta\n", encoding="utf-8")
    assert load_words(path) == ["zeta", "alpha"]


def test_suggest_fixes_common_misspelling(words):
    assert suggest("recieve", words)[0] == "receive"


@pytest.mark.parametrize("word", ["hello", "receive", "the", "Hello", " spelling "])
def test_suggest_returns_correct_word_itself(words, word):
    assert suggest(word, words) == [word.strip().lower()]


def test_suggest_ranks_by_distance_then_frequency():
    words = ["cart", "card", "care", "cat"]
    # "cat" is one edit away from "ca"; the rest are two, kept in list order.
    assert suggest("ca", words) == ["cat", "cart", "card", "care"]


def test_suggest_respects_limit_and_max_distance(words):
    assert len(suggest("teh", words, limit=3)) == 3
    assert suggest("xqzvbn", words) == []
    assert suggest("abcd", ["abxy", "abcz"], max_distance=1) == ["abcz"]


def test_cli_prints_suggestions(capsys):
    assert main(["recieve", "hello", "xqzvbn"]) == 0
    lines = capsys.readouterr().out.splitlines()
    assert lines[0].startswith("recieve: receive")
    assert lines[1] == "hello: correct"
    assert lines[2] == "xqzvbn: no suggestions"


def test_cli_reads_stdin(capsys, monkeypatch):
    monkeypatch.setattr("sys.stdin", io.StringIO("misteak\n"))
    assert main([]) == 0
    assert capsys.readouterr().out == "misteak: mistake\n"


def test_cli_rejects_missing_word_list(tmp_path):
    with pytest.raises(SystemExit) as error:
        main(["--words-file", str(tmp_path / "missing.txt"), "word"])
    assert error.value.code == 2
