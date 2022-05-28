import json
from pathlib import Path
from typing import Iterable
from .document import Document
from io import StringIO


class JsonFileDocument(Document):
    def __init__(self, id: int, path: Path):
        super().__init__(id)
        self.path = path

    @property
    def title(self) -> str:
        file = open(self.path)
        title = file["title"]
        return self.path.stem

    def get_content(self) -> Iterable[str]:
        with open(self.path) as jsonfile:
            content = StringIO(jsonfile['body'])
            return content

    @staticmethod
    def load_from(abs_path: Path, doc_id: int) -> 'JsonFileDocument':
        """A factory method to create a TextFileDocument around the given file path."""
        return JsonFileDocument(doc_id, abs_path)


