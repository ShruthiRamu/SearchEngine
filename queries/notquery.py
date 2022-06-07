from typing import List

from indexes import Index, Posting
from queries import QueryComponent
from text import TokenProcessor


class NotQuery(QueryComponent):
    """NotQuery objects are negative (all others are positive), and the AndQuery is programmed to do an
    "AND NOT" merge if one of its child components is a negative query. """
    def __init__(self, component: QueryComponent):
        self.component = component  # just a single component

    def __init__(self, component: QueryComponent, is_negative: bool):
        self.component = component
        self.is_negative = is_negative

    def get_postings(self, index: Index, token_processor: TokenProcessor) -> List[Posting]:
        result = [Posting]

        # get the postings for the component
        result = self.component.get_postings(index, token_processor)

        return result

    def __str__(self):
        return "NOT ".join(self.component)
