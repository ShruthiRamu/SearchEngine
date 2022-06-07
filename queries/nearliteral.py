from typing import List

import merge_posting
from indexes.postings import Posting
from text import TokenProcessor
from . import TermLiteral
from .querycomponent import QueryComponent


class NearLiteral(QueryComponent):
    """
    Represents a phrase literal consisting of one or more terms that must occur in sequence.
    """

    def __init__(self, terms: List[str], is_negative: bool):
        self.terms = [s for s in terms]
        self.is_negative = is_negative

    # added this to handle single phrase with terms separated by whitespace
    def __init__(self, term: str, is_negative: bool):
        self.terms = term.split(" ")
        self.first_token = self.terms[0]
        self.k = int(self.terms[1].split('/')[1])
        self.second_token = self.terms[2]
        self.is_negative = is_negative

    def get_postings(self, index, token_processor: TokenProcessor) -> List[Posting]:
        result = [Posting]
        merge_function = merge_posting

        first_token_postings = TermLiteral(self.first_token, False).get_postings(index=index, token_processor=token_processor)
        second_token_postings = TermLiteral(self.second_token, False).get_postings(index=index, token_processor=token_processor)

        postings = merge_function.near_k_merge(first_token_postings, second_token_postings, self.k)

        # postings = []
        # k_list = []
        # for term in self.terms:
        #     if term.startswith(('NEAR', 'near', 'Near')):
        #         # get k and add it to the list
        #         k = term.split("/")[1]
        #         k_list.append(int(k))
        #     else:
        #         posting = TermLiteral(term, False).get_postings(index=index, token_processor=token_processor)
        #         postings.append(posting)

        # print("In Near Query component with tokenized query: ", postings)
        # print("K's in the near query: ", k_list)

        # posting1 = postings[0]
        # j = 0
        # for i in range(1, len(postings)):
        #     # get the postings for each component
        #     posting2 = postings[i]
        #     # print("First posting: ")
        #     # for post in posting1:
        #     #     print(post)
        #     # print("Second posting: ")
        #     # for post in posting2:
        #     #     print(post)
        #     # print("------------------------------")
        #     posting1 = merge_function.near_k_merge(posting1, posting2, k_list[j])
        #     j += 1

        # doc_ids = [p.doc_id for p in postings]
        # print(f"Doc IDs:{doc_ids}")
        # print('*' * 80)

        result = postings
        return result

    def __str__(self) -> str:
        return '"' + " ".join(self.terms) + '"'
