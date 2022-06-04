from typing import List, Iterable

import merge_posting
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
        mergedList = [Posting]
        merge_function = merge_posting

        for term in self.terms:
            print("Term: ", term)
            term_literal = TermLiteral(term, False)
            posting = term_literal.get_postings(index, token_processor=token_processor)
            # posting = index.get_postings(term=term)
            componentPostings.append(posting)

        posting1 = componentPostings[0]
        for i in range(1, len(componentPostings)):
            # get the postings for each component
            posting2 = componentPostings[i]
            # print("First posting: ")
            # for post in posting1:
            #     print(post)
            # print("Second posting: ")
            # for post in posting2:
            #     print(post)
            # print("------------------------------")
            posting1 = merge_function.merge_phrase(posting1, posting2, offset=i)

        # doc_ids = [p.doc_id for p in posting1]
        # print(f"Doc IDs:{doc_ids}")
        # print('*' * 80)

        result = posting1

        # Do pairwise folding and merging
        # it = iter(componentPostings)
        # value = next(it)
        # #print("first value: ", value)
        # i = 1
        # for element in it:
        #     #value = merge_function.merge_phraseliterals(value, element, difference=i)
        #     print("In the phrase literal", value)
        #     print("In the phrase literal", element)
        #     value = merge_function.merge_phrase(value, element, offset=i)
        #     i += 1
        #
        # #print("Merged List using custom reduce() for Phrase Literal: ", value)
        #
        # #for result_posting in value:
        # #    print(result_posting, "\n-------------")
        #
        # result = value

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
