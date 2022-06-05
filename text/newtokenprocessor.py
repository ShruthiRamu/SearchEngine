from .tokenprocessor import TokenProcessor
import re
from typing import Iterable
from porter2stemmer import Porter2Stemmer


class NewTokenProcessor(TokenProcessor):
    whitespace_re = re.compile(r"\W+")

    def process_token(self, token: str) -> list:
        stemmer = Porter2Stemmer()
        new_token = token
        new_token2 = ""
        hyphen = False
        all_tokens = []
        while len(new_token) > 0 and not new_token[0].isalnum():
            new_token = new_token[1:]
        while len(new_token) > 0 and not new_token[-1].isalnum():
            new_token = new_token[0:-1]
        for i in new_token:
            if i != self.whitespace_re and i != "'" and i != '"':
                new_token2 += i.lower()
            if i == '-':
                hyphen = True
        if hyphen:
            all_tokens.append(re.sub("-", "", new_token2))
            all_tokens = all_tokens + new_token2.split("-")

            for i in range(1, len(all_tokens)):
                all_tokens[i] = stemmer.stem(all_tokens[i])
        else:
            all_tokens.append(new_token2)
            all_tokens[0] = stemmer.stem(all_tokens[0])
        return all_tokens
