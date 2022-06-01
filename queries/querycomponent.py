from abc import ABC, abstractmethod
from indexes import Posting
from typing import List


class QueryComponent(ABC):
    """
    A QueryComponent is one piece of a larger query, whether that piece is a literal string or represents a merging of
    other components. All nodes in a query parse tree are QueryComponent objects.
    """
    def __init__(self, is_negative=False):
        # Indicates whether it is a negative (only NOT) query
        self.is_negative = is_negative

    @abstractmethod
    def get_postings(self, index) -> List[Posting]:
        """
        Retrieves a list of postings for the query component, using an Index as the source.
        """
        pass