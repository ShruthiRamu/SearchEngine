from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

"""This basic program builds a positionalinvertedindex over the .txt files in 
the same directory as this file."""

def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    index = PositionalInvertedIndex()
    # Iterate through the documents in the corpus:
    for d in corpus:
        # Tokenize each document's content,
        stream = EnglishTokenStream(d.get_content())
        position = 1
        print(f"\nDoc ID: {d.id}")
        for token in stream:
            # Process each token.
            term = token_processor.process_token(token)
            print(f"Term: {term}, Position: {position}")
            index.add_term(term=term, position=position, doc_id=d.id)
            position += 1
    return index


if __name__ == "__main__":
    corpus_path = Path()
    corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(corpus)

    term = "new"
    print(f"\nTerm:{term}")
    for posting in index.get_positional_postings(term):
        print(posting)

    term = "york"
    print(f"\nTerm:{term}")
    for posting in index.get_positional_postings(term):
        print(posting)

    term = "in"
    print(f"\nTerm:{term}")
    for posting in index.get_positional_postings(term):
        print(posting)

