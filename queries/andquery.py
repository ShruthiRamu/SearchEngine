from functools import reduce
from typing import List

import merge_posting
from text import TokenProcessor
from .querycomponent import QueryComponent
from indexes import Index, Posting

from queries import querycomponent


class AndQuery(QueryComponent):
    def __init__(self, components: List[QueryComponent]):
        self.components = components

    def get_postings(self, index: Index, token_processor: TokenProcessor) -> List[Posting]:
        result = [Posting]
        # TODO: program the merge for an AndQuery, by gathering the postings of the composed QueryComponents and
        # intersecting the resulting postings.

        componentPostings = []
        mergedList = [Posting]
        merge_function = merge_posting

        # You can use your own merge with reduce:
        #
        # from functools import reduce
        #
        # l = [[8, 10, 12], [4, 5, 9], [2, 11]]
        #
        # merged = reduce(merge, l)
        # print(merged)
        # # [2, 4, 5, 8, 9, 10, 11, 12]
        # "in new" - university + york
        posting1 = self.components[0].get_postings(index, token_processor)
        is_negative = self.components[0].is_negative
        for i in range(1, len(self.components)):
            # get the postings for each component
            posting2 = self.components[i].get_postings(index, token_processor)
            # Check the negatives
            #if not self.components[i].is_negative:
            if is_negative:
                # Swap the posting we passed to function
                # Call not merge
                print("Found a Not query: ")
                # for posting in second:
                #     print(posting)
                posting1 = merge_function.and_not_merge(posting2, posting1)
            if self.components[i].is_negative:
                # Call not merge
                posting1 = merge_function.and_not_merge(posting1, posting2)

            else:
                # Regualr
                posting1 = merge_function.and_merge(posting1, posting2)




            # if not is_negative:
            #     first = posting1
            #     second = posting2
            #     posting1 = merge_function.and_merge(first, second)
            # else:
            #     first = posting2
            #     second = posting1 # not posting
            #     print("Found a Not query: ")
            #     for posting in second:
            #         print(posting)
            #     posting1 = merge_function.and_not_merge(first, second)



        # for component in self.components:
        #
        #     #print("Got a Not query: ", component)
        #
        #     # get the postings for each component
        #     posting = component.get_postings(index, token_processor)
        #     componentPostings.append(posting)
        #     # Check for negative terms and put all the negative terms to the end or as the second term, don't make it
        #     # the first component
        #
        #     # Do pairwise folding and merging
        #     it = iter(componentPostings)
        #     value = next(it)
        #     print("first value: ", value)
        #     i = 1
        #     for element in it:
        #         value = merge_function.merge_phraseliterals(value, element, difference=i)
        #         i += 1
        #
        # #merged_list = reduce(merge_function.and_merge, componentPostings)
        # print("Merged List using custom reduce() for and query: ", merged_list)
        #
        # for result_posting in merged_list:
        #     print(result_posting)

        #result = merged_list
        result = posting1

        # #  do pairwise intersection
        # if len(componentPostings) >= 2:
        #     first = componentPostings[0]
        #     second = componentPostings[1]
        #
        #
        #     mergedList = merge_function.merge(first, second, 'and') # may be use whitespace or + for OR instead of the str
        #
        #     i = 2  # continue with next index
        #
        #     while i < len(componentPostings):
        #         updatedList = merge_function.merge(mergedList, componentPostings[i], 'and')
        #         mergedList = updatedList
        #         i += 1
        #
        # result = mergedList
        return result

    def __str__(self):
        return " AND ".join(map(str, self.components))
