from typing import List

import merge_posting
from indexes import Index, Posting
from queries import QueryComponent


class NotQuery(QueryComponent):
    def __init__(self, components: List[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index) -> List[Posting]:
        result = [Posting]
        # TODO: program the merge for an NotQuery, by gathering the postings of the composed QueryComponents and
        # intersecting the resulting postings.

        componentPostings = []
        mergedList = [Posting]
        merge_function = merge_posting

        # TODO: Finish NotQuery merging logic

        result = mergedList
        return result

    def __str__(self):
        return " NOT ".join(map(str, self.components))

