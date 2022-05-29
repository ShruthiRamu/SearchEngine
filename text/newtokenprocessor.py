from curses.ascii import isalnum
from .tokenprocessor import TokenProcessor
import re
from typing import Iterable
from porter2stemmer import Porter2Stemmer


class NewTokenProcessor(TokenProcessor):
    whitespace_re = re.compile(r"\W+")

    def process_token(self, token: str) -> Iterable[str]:
        stemmer = Porter2Stemmer()
        new_token = token
        new_token2 = ""
        hyphen = False
        all_tokens = []
        if not isalnum(new_token[0]):
            new_token = new_token[1:]
        if not isalnum(new_token[-1]):
            new_token = new_token[0:-2]
        for i in new_token:
            if i != self.whitespace_re and i != "'" and i != '"':
                new_token2 += i.lower()
            if i == '-':
                hyphen = True
        if hyphen:
            all_tokens = new_token2.split("-")
            all_tokens.append(re.sub("-", "", new_token2))
        else:
            all_tokens.append(new_token2)
        for i in range(len(all_tokens)):
            all_tokens[i] = stemmer.stem(all_tokens[i])
        return all_tokens
