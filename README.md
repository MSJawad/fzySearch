# fzySearch

[![CI](https://github.com/MSJawad/fzySearch/actions/workflows/ci.yml/badge.svg?branch=master)](https://github.com/MSJawad/fzySearch/actions/workflows/ci.yml)

A small spellchecker in pure Python. It suggests corrections for a word by
computing its [Levenshtein edit distance](https://en.wikipedia.org/wiki/Levenshtein_distance)
to every word in a list of about 10,000 common English words, then ranking the
close matches by distance and by how common they are.

```console
$ python -m fzysearch recieve speling hello xqzvbn
recieve: receive, believe, recipe, retrieve
speling: spelling, spring, selling, opening, seeking
hello: correct
xqzvbn: no suggestions
```

## Quick start

Requires Python 3.9 or newer and has no dependencies. From a clone of the
repository:

```sh
python -m fzysearch recieve
```

Words can also be piped in on standard input:

```sh
echo "definately seperate" | python -m fzysearch
```

To install the `fzysearch` command:

```sh
pip install .
fzysearch accomodate
```

Options:

| Option | Default | Meaning |
| --- | --- | --- |
| `-d`, `--max-distance` | 2 | largest edit distance to suggest |
| `-n`, `--limit` | 5 | most suggestions to show per word |
| `-w`, `--words-file` | bundled list | your own word list, one word per line, most frequent first |

## Using it from Python

```python
from fzysearch import edit_distance, load_words, suggest

words = load_words()                # bundled list, most frequent first
suggest("recieve", words)           # ['receive', 'believe', 'recipe', 'retrieve']
suggest("hello", words)             # ['hello'], a correct word returns itself
edit_distance("kitten", "sitting")  # 3
```

`suggest(word, words, max_distance=2, limit=5)` returns at most `limit` words
within `max_distance` edits, closest first. Ties keep the order of `words`, so a
frequency-ordered list puts common words ahead of rare ones.

## How it works

The edit distance between two words is the fewest single-character insertions,
deletions and substitutions that turn one into the other. It is computed with
the [Wagner-Fischer algorithm](https://en.wikipedia.org/wiki/Wagner%E2%80%93Fischer_algorithm):
a table where cell `(i, j)` holds the distance between the first `i` letters of
one word and the first `j` letters of the other. Each cell is the smallest of

- the cell above plus one (a deletion),
- the cell to the left plus one (an insertion),
- the cell diagonally above-left, plus one if the two letters differ (a substitution or a match).

The bottom-right cell is the answer. Only the previous row is needed to fill
the next one, so the implementation keeps two rows instead of the whole table.

Most of the 10,000 words are far from the query, so `suggest` skips work in two
ways. A word whose length differs from the query by more than `max_distance`
cannot be close enough and is rejected without building a table. Otherwise the
table stops early once every cell in a row exceeds `max_distance`, because the
final distance can only be larger.

## Word list

[`fzysearch/words.txt`](fzysearch/words.txt) is
`google-10000-english-no-swears.txt` from Josh Kaufman's
[google-10000-english](https://github.com/first20hours/google-10000-english):
the 10,000 most frequent words in Google's Web Trillion Word Corpus, via
[Peter Norvig's word counts](https://norvig.com/ngrams/), with swear words
removed. The list is in order of frequency, which is what the ranking relies on.
It is a list of common words, not of misspellings, so rare or technical words
are reported as misspelled. Pass `--words-file` to use a different list.

## Development

```sh
pip install -e ".[test]"
pytest
```

## License

The code is released under the [MIT License](LICENSE). The word list is not
covered by it: it carries the terms of its
[source](https://github.com/first20hours/google-10000-english/blob/master/LICENSE.md),
which permit educational, personal and research use.

## Author

Mohammad Solaiman Jawad
