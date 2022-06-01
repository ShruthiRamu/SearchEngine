from typing import Iterable
from . import Posting, Index


class PositionalInvertedIndex(Index):

    def __init__(self):
        # Maps Term to postings lists of pairs (docID, [position1, position2, ...])
        self._dictionary = {}

    def add_term(self, term: str, position: int, doc_id: int):
        """ Record position posting for the term """
        if term in self._dictionary.keys():
            postings = self._dictionary[term]
            if postings[-1].doc_id == doc_id: # Same term again in same document
                postings[-1].positions.append(position) # Record where it appears
            elif postings[-1].doc_id != doc_id: # Same Term in new document
                postings.append(Posting(doc_id=doc_id, position=position)) # Record a new posting
        else:
            self._dictionary[term] = [Posting(doc_id=doc_id, position=position)] # New term -> posting

    def get_postings(self, term: str) -> Iterable[Posting]:
        """ Returns a list of Postings for all documents that contain the given term. """
        return self._dictionary[term] if term in self._dictionary.keys() else []

    def vocabulary(self) -> Iterable[str]:
        """ Returns a sorted vocabulary list """
        """ Returns a sorted vocabulary list """
        vocab = list(self._dictionary.keys())
        vocab.sort()
        return vocab