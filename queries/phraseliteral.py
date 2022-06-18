from typing import List, Iterable

import merge_posting
from indexes.invertedindex import InvertedIndex
from indexes.postings import Posting
from text import TokenProcessor
from . import TermLiteral
from .querycomponent import QueryComponent


class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms: List[str], is_negative: bool):
        self.terms = [s for s in terms]
        self.is_negative = is_negative

    # added this to handle single phrase with terms separated by whitespace
    def __init__(self, term: str, is_negative: bool):
        self.terms = term.split(" ")
        self.is_negative = is_negative

    def get_postings(self, index, token_processor: TokenProcessor) -> List[Posting]:
        result = [Posting]
        componentPostings = []
        merge_function = merge_posting

        # Handle if biword index
        if isinstance(index, InvertedIndex) and len(self.terms) == 2:
            # Assuming the first term the token processor always returns the pair value
            first_tokenized_terms = token_processor.process_token(self.terms[0])
            second_tokenized_terms = token_processor.process_token(self.terms[1])
            tokenized_query_term_1 = first_tokenized_terms[0]
            tokenized_query_term_2 = second_tokenized_terms[0]
            biword_term = tokenized_query_term_1 + ' ' + tokenized_query_term_2
            posting = index.get_postings(biword_term)
            return list(posting)



        # Handle longer phrase queries
        for term in self.terms:
            term_literal = TermLiteral(term, False)
            posting = term_literal.get_postings(index, token_processor=token_processor)
            componentPostings.append(posting)

        posting1 = componentPostings[0]
        for i in range(1, len(componentPostings)):
            # get the postings for each component
            posting2 = componentPostings[i]
            posting1 = merge_function.merge_phrase(posting1, posting2, offset=i)

        result = posting1

        return result

    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'
