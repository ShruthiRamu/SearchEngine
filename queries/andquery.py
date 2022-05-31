from typing import List

import merge_posting
from .querycomponent import QueryComponent
from indexes import Index, Posting

from queries import querycomponent


class AndQuery(QueryComponent):
    def __init__(self, components: List[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index) -> List[Posting]:
        result = [Posting]
        # TODO: program the merge for an AndQuery, by gathering the postings of the composed QueryComponents and
        # intersecting the resulting postings.

        componentPostings = []
        mergedList = [Posting]
        merge_function = merge_posting

        for component in self.components:
            # get the postings for each component
            posting = component.get_postings(index)
            componentPostings.append(posting)

        #  do pairwise intersection
        # TODO: Yet to fix this to work as expected
        if len(componentPostings) >= 2:
            first = componentPostings[0]
            second = componentPostings[1]
            mergedList = merge_function.merge(first, second, 'and')

            i = 2  # continue with next index

            while i < len(componentPostings):
                updatedList = merge_function.merge(mergedList, componentPostings[i], 'and')
                mergedList = updatedList
                i += 1

        result = mergedList
        return result

    def __str__(self):
        return " AND ".join(map(str, self.components))
