class Posting:
    """A Posting encapulates a document ID associated with a search query component."""
    def __init__(self, doc_id : int, position: int):
        self.doc_id = doc_id
        self.positions = [position]
    def __str__(self):
        return f"(ID: {self.doc_id }, {[pos for pos in self.positions]})"