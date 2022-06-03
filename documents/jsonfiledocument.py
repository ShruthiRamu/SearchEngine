import json
from io import StringIO
from pathlib import Path
from typing import Iterable
from .document import Document


class JsonFileDocument(Document):
    """
    Represents a document that is a json file read from the local file system.
    """

    def __init__(self, id: int, path: Path):
        super().__init__(id)
        self.path = path


    def get_file_name(self) -> str:
        return self.path.stem


    # returns a string
    def get_title(self) -> str:
        # Opening JSON file
        f = open(self.path, encoding="utf8")

        # returns JSON object as
        # a dictionary
        data = json.load(f)

        # Get the title of the json
        title = data['title']

        # Closing file
        f.close()
        return title

    def get_author(self) -> str:
        f = open(self.path, encoding="utf8")
        data = json.load(f)
        author = data['author']
        f.close()
        return author

    @property
    def title(self) -> str:
        title = self.get_title()
        return title

    # returns TextIOWrapper
    def get_content(self) -> Iterable[str]:
        # Opening JSON file
        f = open(self.path, encoding="utf8")

        # returns JSON object as
        # a dictionary
        data = json.load(f)

        content = StringIO(data['body'])

        # Closing file
        f.close()

        return content.readlines()

    @staticmethod
    def load_from(abs_path: Path, doc_id: int) -> 'JsonFileDocument':
        """A factory method to create a JsonFileDocument around the given file path."""
        return JsonFileDocument(doc_id, abs_path)