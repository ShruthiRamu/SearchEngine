from typing import List

import merge_posting
from indexes.postings import Posting
from text.newtokenprocessor import NewTokenProcessor
from .querycomponent import QueryComponent
from indexes.positionalinvertedindex import PositionalInvertedIndex

class PhraseLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms : List[str]):
        self.terms = [s for s in terms]

    # added this to handle single phrase with terms separated by whitespace
    def __init__(self, term : str):
        self.terms = term.split(" ")

    def get_postings(self, index) -> List[Posting]:
        result = [Posting]
        componentPostings = []
        mergedList = [Posting]
        merge_function = merge_posting
        tokenProcessor = NewTokenProcessor()

        for term in self.terms:
            # TODO: Confirm whether to process token here just before calling the index to get postings
            #  tokenProcessor.process_token(term)
            posting = index.get_postings(term=term)
            componentPostings.append(posting)

        # do pairwise positional merge
        # TODO: Yet to fix this to work as expected
        if len(componentPostings) >= 2 and (componentPostings[0] is not None) and (componentPostings[1] is not None):
            first = componentPostings[0]
            second = componentPostings[1]
            mergedList = merge_function.merge_phraseliterals(first, second, difference=1)

            i = 2  # begin with next index

            while i < len(componentPostings):
                updatedList = merge_function.merge_phraseliterals(mergedList, componentPostings[i], difference=i)
                #mergedList = merge_function.merge_phraseliterals(mergedList, componentPostings[i], difference=i)
                mergedList = updatedList
                i += 1

        result = mergedList
        return result
        # TODO: program this method. Retrieve the postings for the individual terms in the phrase,
		# and positional merge them together.



    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'