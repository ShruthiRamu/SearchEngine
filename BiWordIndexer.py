from itertools import tee
from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.biwordindex import BiWordIndex
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

"""This basic program builds a biwordindex over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    index = BiWordIndex()
    # Iterate through the documents in the corpus:
    for d in corpus:
        # Tokenize each document's content,
        stream = EnglishTokenStream(d.get_content())
        print(f"\nDoc ID: {d.id}")
        # list(itertools.pairwise(stream))

        for current, next in pairwise(stream):
            # print(f'Current = {current}, next = {next}')
            # tokenize both the terms
            current = token_processor.process_token(current)
            next = token_processor.process_token(next)

            # concatenate them as a single term
            term = current + ' ' + next
            index.add_term(term=term, doc_id=d.id)
    return index


def pairwise(iterable):
    # "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


if __name__ == "__main__":
    corpus_path = Path()
    corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(corpus)

    term = "new york"
    print(f"\nTerm:{term}")
    for posting in index.get_postings(term):
        print(posting)

    term = "york university"
    print(f"\nTerm:{term}")
    for posting in index.get_postings(term):
        print(posting)

    term = "in new"
    print(f"\nTerm:{term}")
    for posting in index.get_postings(term):
        print(posting)
