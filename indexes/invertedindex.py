from typing import Iterable
from . import Posting, Index

class InvertedIndex(Index):

    def __init__(self):
        # Mapping of Term (str) to List of Posting
        self._dictionary = {}

        # Can also use:
        #   self._dictionary = defaultdict(set)


    def add_term(self, term: str, doc_id: int):
        """ Record a posting of the term """
        if term in self._dictionary.keys():
            postings = self._dictionary[term]
            # postings sorted
            if postings[-1].doc_id != doc_id: # No duplicate of doc_id for same term
                # If the postings of term already exists, add doc_id to the end of postings list
                postings.append(Posting(doc_id=doc_id))
        else:
            self._dictionary[term] = [Posting(doc_id=doc_id)]
        # Can also do :
        #         self._dictionary[term].add(Posting(doc_id))

    def get_postings(self, term: str) -> Iterable[Posting]:
        """Returns a list of Postings for all documents that contain the given term."""
        return self._dictionary[term] if term in self._dictionary.keys() else []
        # Can also do
        #        return self._dictionary[term]


    def vocabulary(self) -> Iterable[str]:
        """Returns a sorted vocabulary list"""
        return list(self._dictionary.keys()).sort()
