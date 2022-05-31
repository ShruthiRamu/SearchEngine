from typing import Iterable
from . import Posting, Index


class SoundexIndex(Index):
    def __init__(self):
        # Soundex Code -> [Term]
        self._dictionary = {}

    def add_term(self, code: str, term: str):
        """ Records the term for soundex code """
        if code in self._dictionary.keys():
            self._dictionary[code].append(term)
        else:
            self._dictionary[code] = [term]

    def get_postings(self, term: str) -> Iterable[Posting]:
        """ Returns a list of Postings for all documents that contain the given term. """
        return self._dictionary[term] if term in self._dictionary.keys() else []

    def vocabulary(self) -> Iterable[str]:
        """ Returns a sorted vocabulary list """
        return list(self._dictionary.keys()).sort()