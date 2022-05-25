from ast import Str
import os
from pyclbr import Function
from typing import Callable, Iterable, Iterator

from documents.document import Document
from . import textfiledocument
from pathlib import Path

class DirectoryCorpus:
    """A DirectoryCorpus represents a corpus found in a single directory on a local file system."""
    
    def __init__(self, abs_path : Path, file_filter : Callable[[Path], bool] = lambda p: True, factories : dict[str, Callable[[str], Document]] = {}):
        """
        Constructs a corpus over an absolute directory path.

        It is recommended that you use the static method load_text_directory rather than construct a DirectoryCorpus directly.
        
        :param Path abs_path: the absolute path of the directory to load.
        :param file_filter: a predicate function, identifying whether to load a particular file Path found in the corpus. Defaults to always returning True.
        :param dict factories: a dictionary of factory functions, mapping from a file extension (like .txt) to a function that constructs a Document-derived object for a given Path parameter.
        """
        self.corpus_path = abs_path
        self.file_filter = file_filter
        self.factories = factories
        self._documents = None

    def documents(self) -> Iterable[Document]:
        if self._documents is None:
            self._documents = self._read_documents()
        return self._documents.values()

    def __iter__(self) -> Iterator[Document]:
        return iter(self.documents())

    def __len__(self) -> int:
        if self._documents is None:
            self._documents = self._read_documents()
        return len(self._documents)

    def get_document(self, doc_id) -> Document:
        return self._documents[doc_id]

    def _read_documents(self) -> list[Document]:
        files = list(Path(self.corpus_path).glob("*"))
        results = {}
        next_id = 0
        for f in files:
            if f.suffix in self.factories and self.file_filter(f):
                results[next_id] = self.factories[f.suffix](f, next_id)
                next_id += 1
        return results

    @staticmethod
    def load_text_directory(path, extension) -> 'DirectoryCorpus':
        c = DirectoryCorpus(path, 
                lambda f: f.suffix == extension, 
                factories={extension: textfiledocument.TextFileDocument.load_from})
        return c
