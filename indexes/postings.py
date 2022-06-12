class Posting:
    """A Posting encapulates a document ID associated with a search query component."""
    def __init__(self, doc_id : int, tftd:int= -1, position:int =-1):
        self.doc_id = doc_id
        self.tftd = tftd
        self.positions = [] if position == -1 else [position]

    def __str__(self):
        if self.positions:
            return f"(ID: {self.doc_id }, -> {[pos for pos in self.positions]})"
        if self.tftd:
            return f"(ID: {self.doc_id }, -> Term Frequency: {self.tftd})"
        return str(self.doc_id)