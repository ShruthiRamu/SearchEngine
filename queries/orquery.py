from functools import reduce
from typing import List

import merge_posting
from text import TokenProcessor
from .querycomponent import QueryComponent
from indexes import Index, Posting


class OrQuery(QueryComponent):
    def __init__(self, components: List[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index, token_processor: TokenProcessor) -> List[Posting]:
        result = []
        # TODO: program the merge for an OrQuery, by gathering the postings of the composed QueryComponents and
        # merging the resulting postings.

        componentPostings = []
        mergedList = [Posting]
        merge_function = merge_posting

        # get postings for all the components
        for component in self.components:
            posting = component.get_postings(index, token_processor)
            componentPostings.append(posting)

        merged_list = reduce(merge_function.or_merge, componentPostings)
        # print("Merged List using reduce() for OR query: ", merged_list)

        # for result_posting in merged_list:
        #    print(result_posting, "\n-------------")

        result = merged_list

        # do pairwise merging of the postings
        # if len(componentPostings) >= 2:
        #     first = componentPostings[0]
        #     second = componentPostings[1]
        #     mergedList = merge_function.merge(first, second, 'or')
        #
        #     i = 2  # continue with next index
        #
        #     while i < len(componentPostings):
        #         updatedList = merge_function.merge(mergedList, componentPostings[i], 'or')
        #         mergedList = updatedList
        #         i += 1
        #
        # result = mergedList
        return result

    def __str__(self):
        return "(" + " OR ".join(map(str, self.components)) + ")"
