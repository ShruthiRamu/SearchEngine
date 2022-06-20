from typing import List

import merge_posting
from indexes.postings import Posting
from text import TokenProcessor
from . import TermLiteral
from .querycomponent import QueryComponent


class NearLiteral(QueryComponent):
    """
    Represents a near literal consisting of one or more terms that must occur in sequence. Given a value k,
    this does a positional merge between the terms to the left and right of the NEAR operator, selecting documents
    where the second term appears at most k positions away from the first term.
    """

    def __init__(self, terms: List[str], is_negative: bool):
        self.terms = [s for s in terms]
        self.is_negative = is_negative

    def __init__(self, term: str, is_negative: bool):
        self.terms = term.split(" ")
        self.first_token = self.terms[0]
        self.k = int(self.terms[1].split('/')[1])
        self.second_token = self.terms[2]
        self.is_negative = is_negative

    def get_postings(self, index, token_processor: TokenProcessor) -> List[Posting]:
        result = [Posting]
        merge_function = merge_posting

        first_token_postings = TermLiteral(self.first_token, False, mode='boolean').get_postings(index=index, token_processor=token_processor)
        second_token_postings = TermLiteral(self.second_token, False, mode='boolean').get_postings(index=index, token_processor=token_processor)

        postings = merge_function.near_k_merge(first_token_postings, second_token_postings, self.k)

        result = postings
        return result

    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'
