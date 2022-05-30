from pathlib import Path

from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

"""This basic program builds a term-document matrix over the .txt files in 
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

    #  term = '"new york university"' --- Phrase Literal
    #  term = "new york" ---And query
    term = "new + york"  # ---Or query
    print(f"\nTerm:{term}")

    booleanqueryparser = BooleanQueryParser()
    # parse the given query and print the postings
    querycomponent = booleanqueryparser.parse_query(query=term)
    for posting in querycomponent.get_postings(index):
        print(posting)

    term = "new"
    print(f"\nTerm:{term}")
    querycomponent = booleanqueryparser.parse_query(term)
    for posting in querycomponent.get_postings(index):
        print(posting)

    term = "york"
    print(f"\nTerm:{term}")
    querycomponent = booleanqueryparser.parse_query(term)
    for posting in index.get_postings(term):
        print(posting)

    term = "in"
    print(f"\nTerm:{term}")
    querycomponent = booleanqueryparser.parse_query(term)
    for posting in index.get_postings(term):
        print(posting)

