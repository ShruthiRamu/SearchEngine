from typing import List

from indexes.postings import Posting
from text import TokenProcessor, BasicTokenProcessor
from text.newtokenprocessor import NewTokenProcessor
from .querycomponent import QueryComponent


class TermLiteral(QueryComponent):
    """
    A TermLiteral represents a single term in a subquery.
    """

    def __init__(self, term: str, is_negative: bool, mode: str):
        self.term = term
        self.is_negative = is_negative
        self.mode = mode

    def get_postings(self, index, token_processor: TokenProcessor) -> List[Posting]:
        tokenized_term = token_processor.process_token(token=self.term)
        is_hyphenated = False
        if '-' in self.term:
            tokenized_term = tokenized_term[0]
            is_hyphenated = True
        postings = []
        postings_list = []
        if isinstance(token_processor, NewTokenProcessor):
            # Do not perform the split on hyphens step on query literals; use the whole literal, including the hyphen.
            if is_hyphenated:
                if self.mode == 'rank':
                    postings = index.get_postings(tokenized_term)
                elif self.mode == 'boolean':
                    postings = index.get_positional_postings(tokenized_term)
            else:
                for term in tokenized_term:
                    # postings.append(index.get_postings(term))
                    # postings = [post for posting in postings for post in posting]
                    if self.mode == 'rank':
                        postings = index.get_postings(term)
                    elif self.mode == 'boolean':
                        postings = index.get_positional_postings(term)
                    # postings_list.append(index.get_postings(term))
                    # postings_list.append(postings)
                    # for posting in postings_list:
                    #     #print("type(posting): ", type(posting))
                    #     if type(posting) is list:
                    #         print("inside type()")
                    #         count = 0
                    #         #print("Posting: ", posting)
                    #         for post in posting:
                    #             print("Post: ", count)
                    #             count += 1
                    #             postings.append(post)
                    #     else:
                    #         postings.append(posting)

        elif isinstance(token_processor, BasicTokenProcessor):
            if self.mode == 'rank':
                postings = index.get_postings(tokenized_term)
            elif self.mode == 'boolean':
                postings = index.get_positional_postings(tokenized_term)
        return postings
        # return index.get_postings(tokenized_term)
        # return index.get_postings(self.term)

    def __str__(self) -> str:
        return self.term
