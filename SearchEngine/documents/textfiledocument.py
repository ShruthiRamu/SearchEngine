from pathlib import Path
from typing import Iterable
from .document import Document
class TextFileDocument(Document):
    """
    Represents a document that is saved as a simple text file in the local file system.
    """
    def __init__(self, id : int, path : Path):
        super().__init__(id)
        self.path = path

    @property
    def title(self) -> str:
        return self.path.stem

    # returns TextIOWrapper
    def get_content(self) -> Iterable[str]:
        return open(self.path)

    @staticmethod
    def load_from(abs_path : Path, doc_id : int) -> 'TextFileDocument' :
        """A factory method to create a TextFileDocument around the given file path."""
        return TextFileDocument(doc_id, abs_path)