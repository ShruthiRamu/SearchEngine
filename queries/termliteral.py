from typing import List

from indexes.postings import Posting
from text import BasicTokenProcessor
from .querycomponent import QueryComponent

class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term : str, is_negative: bool):
        self.term = term
        self.is_negative = is_negative

    def get_postings(self, index) -> List[Posting]:

        token_processor = BasicTokenProcessor()
        tokenized_term = token_processor.process_token(self.term)
        print("Tokenized term: ", tokenized_term)
        return index.get_postings(tokenized_term)
        #return index.get_postings(self.term)

    def __str__(self) -> str:
        return self.term