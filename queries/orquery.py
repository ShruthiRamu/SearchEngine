from functools import reduce
from typing import List

import merge_posting
from text import TokenProcessor
from .querycomponent import QueryComponent
from indexes import Index, Posting


class OrQuery(QueryComponent):
    """OrQuery: Consists of a list of Querys, and answers getPostings by getting the postings of its components and
    performing the "OR merge" routine """
    def __init__(self, components: List[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index, token_processor: TokenProcessor) -> List[Posting]:
        result = []
        # TODO: program the merge for an OrQuery, by gathering the postings of the composed QueryComponents and
        # merging the resulting postings.

        componentPostings = []
        merge_function = merge_posting

        # get postings for all the components
        for component in self.components:
            posting = component.get_postings(index, token_processor)
            componentPostings.append(posting)

        merged_list = reduce(merge_function.or_merge, componentPostings)

        result = merged_list
        return result

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"
