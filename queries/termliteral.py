from typing import List

from indexes.postings import Posting
from text import TokenProcessor, BasicTokenProcessor
from text.newtokenprocessor import NewTokenProcessor
from .querycomponent import QueryComponent


class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term: str, is_negative: bool):
        self.term = term
        self.is_negative = is_negative

    def get_postings(self, index, token_processor: TokenProcessor) -> List[Posting]:
        tokenized_term = token_processor.process_token(token=self.term)
        postings = []
        if isinstance(token_processor, NewTokenProcessor):
            for term in tokenized_term:
                print("Tokenized query: ", term)
                postings.append(index.get_postings(term))
                postings = [post for posting in postings for post in posting]

        elif isinstance(token_processor, BasicTokenProcessor):
            postings = index.get_postings(tokenized_term)
        # print("Tokenized query term: ", tokenized_term)
        return postings
        # return index.get_postings(tokenized_term)
        # return index.get_postings(self.term)

    def __str__(self) -> str:
        return self.term
