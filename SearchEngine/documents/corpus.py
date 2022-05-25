from abc import ABC, abstractmethod
from typing import Iterable

from .document import Document

class DocumentCorpus(ABC):
    """Represents a collection of documents used to build an index."""

    @abstractmethod
    def documents(self) -> Iterable[Document]:
        """Gets all documents in the corpus."""
        pass

    @abstractmethod
    def __len__(self) -> int:
        """The number of documents in the corpus."""
        pass

    @abstractmethod
    def get_document(self, doc_id) -> Document:
        """Returns the document with the given document ID."""
        pass


    def __iter__(self) -> Iterable[Document]:
        pass

