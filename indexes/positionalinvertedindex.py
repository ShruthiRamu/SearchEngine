from typing import Iterable
from pathlib import Path
from . import Posting, Index
from documents import DirectoryCorpus
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

class PositionalInvertedIndex(Index):

    def __init__(self):
        # Maps Term to postings lists of pairs (docID, [position1, position2, ...])
        self._dictionary = {}

    def add_term(self, term: str, position: int, doc_id: int):
        " Record position posting for the term"
        if term in self._dictionary.keys():
            postings = self._dictionary[term]
            if postings[-1].doc_id == doc_id: # Same Term shows up again in same document
                # Record the position where it appears
                postings[-1].positions.append(position)
            elif postings[-1].doc_id != doc_id: # Same Term shows up in new document
                # Record a new posting
                postings.append(Posting(doc_id=doc_id, position=position))
        else:
            # New term in dictionary
            self._dictionary[term] = [Posting(doc_id=doc_id, position=position)]

    def get_postings(self, term: str) -> Iterable[Posting]:
        """ Returns a list of Postings for all documents that contain the given term. """
        return self._dictionary[term] if term in self._dictionary.keys() else []

    def vocabulary(self) -> Iterable[str]:
        """ Returns a sorted vocabulary list """
        #TODO: WHEN TO SORT?
        return list(self._dictionary.keys()).sort()
