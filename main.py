from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream
from time import time_ns

def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    index = PositionalInvertedIndex()
    for d in corpus:
        stream = EnglishTokenStream(d.get_content())
        position = 1
        for token in stream:
            term = token_processor.process_token(token)
            index.add_term(term=term, position=position, doc_id=d.id)
            position += 1
    return index

" Main Application of Search Engine "

if __name__ == "__main__":

    # Assuming in cwd
    # dir = input("Enter Directory Name: ")
    # Construct a path
    corpus_path = Path()
    corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    start = time_ns()
    index = index_corpus(corpus)
    end = time_ns()
    print(f"Building Index: {round(end-start, 2)} ns")

    while True:
        query = input("Enter Search Query: ")
        # Handle Special Query

        # Handle Query
        if True:
            break
