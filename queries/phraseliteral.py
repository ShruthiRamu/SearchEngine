from typing import List, Iterable

import merge_posting
from indexes.postings import Posting
from text import TokenProcessor
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
        mergedList = [Posting]
        merge_function = merge_posting

        for term in self.terms:
            tokenized_term = token_processor.process_token(term)
            print("Tokenized query term: ", tokenized_term)
            posting = index.get_postings(term=tokenized_term)

            # posting = index.get_postings(term=term)
            componentPostings.append(posting)

        # Do pairwise folding and merging
        it = iter(componentPostings)
        value = next(it)
        print("first value: ", value)
        i = 1
        for element in it:
            value = merge_function.merge_phraseliterals(value, element, difference=i)
            i += 1

        print("Merged List using custom reduce() for Phrase Literal: ", value)

        for result_posting in value:
            print(result_posting, "\n-------------")

        result = value

        # do pairwise positional merge
        # if len(componentPostings) >= 2 and (componentPostings[0] is not None) and (componentPostings[1] is not None):
        #     first = componentPostings[0]
        #     second = componentPostings[1]
        #     mergedList = merge_function.merge_phraseliterals(first, second, difference=1)
        #
        #     i = 2  # begin with next index
        #
        #     while i < len(componentPostings):
        #         updatedList = merge_function.merge_phraseliterals(mergedList, componentPostings[i], difference=i)
        #         #mergedList = merge_function.merge_phraseliterals(mergedList, componentPostings[i], difference=i)
        #         mergedList = updatedList
        #         i += 1
        #
        # result = mergedList
        return result

    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'
