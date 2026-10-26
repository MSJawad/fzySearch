"""A small Levenshtein-distance spellchecker."""

from .core import WORDS_PATH, edit_distance, load_words, suggest

__all__ = ["WORDS_PATH", "edit_distance", "load_words", "suggest"]
