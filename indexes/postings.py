class Posting:
    """A Posting encapulates a document ID associated with a search query component."""
    def __init__(self, doc_id : int):
        self.doc_id = doc_id
    def __str__(self):
        return str(self.doc_id)
