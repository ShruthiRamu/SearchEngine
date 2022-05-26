from abc import ABC, abstractmethod
from typing import Iterable, List

from .postings import Posting


class Index(ABC):
    """An Index can retrieve postings for a term from a data structure associating terms and the documents
    that contain them."""

    def get_postings(self, term: str) -> Iterable[Posting]:
        """Retrieves a sequence of Postings of documents that contain the given term."""
        pass

    def vocabulary(self) -> List[str]:
        """A (sorted) list of all terms in the index vocabulary."""
        pass
