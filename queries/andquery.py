from typing import List

import merge_posting
from text import TokenProcessor
from .querycomponent import QueryComponent
from indexes import Index, Posting


class AndQuery(QueryComponent):
    """AndQuery: a subquery to represent the "and" ing of two or more terms, an AndQuery holds a list of
    QueryComponent objects. """
    def __init__(self, components: List[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index, token_processor: TokenProcessor) -> List[Posting]:
        result = [Posting]
        # intersecting the resulting postings.

        merge_function = merge_posting

        posting1 = self.components[0].get_postings(index, token_processor)
        is_negative = self.components[0].is_negative
        for i in range(1, len(self.components)):
            # get the postings for each component
            posting2 = self.components[i].get_postings(index, token_processor)
            # Check the negatives
            # if not self.components[i].is_negative:
            if is_negative:
                # Swap the posting we passed to function
                # Call not merge
                posting1 = merge_function.and_not_merge(posting2, posting1)
            if self.components[i].is_negative:
                # Call not merge
                posting1 = merge_function.and_not_merge(posting1, posting2)

            else:
                # Regular
                posting1 = merge_function.and_merge(posting1, posting2)

        result = posting1
        return result

    def __str__(self):
        return " AND ".join(map(str, self.components))
