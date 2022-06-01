from typing import List

import merge_posting
from indexes import Index, Posting
from queries import QueryComponent


class NotQuery(QueryComponent):
    def __init__(self, component: QueryComponent):
        self.component = component  # just a single component

    def get_postings(self, index: Index) -> List[Posting]:
        result = [Posting]

        # get the postings for the component
        result = self.component.get_postings(index)

        return result

    def __str__(self):
        return "NOT ". join(map(self.component))
