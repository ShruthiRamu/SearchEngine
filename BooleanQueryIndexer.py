from pathlib import Path
from time import time_ns

from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream
from text.newtokenprocessor import NewTokenProcessor

"""This basic program builds a positional inverted index over the .txt files in 
the same directory as this file."""

def index_corpus(corpus: DocumentCorpus) -> Index:
    # token_processor = BasicTokenProcessor()
    # index = PositionalInvertedIndex()
    # # Iterate through the documents in the corpus:
    # for d in corpus:
    #     # Tokenize each document's content,
    #     stream = EnglishTokenStream(d.get_content())
    #     position = 1
    #     print(f"\nDoc ID: {d.id}")
    #     for token in stream:
    #         # Process each token.
    #         term = token_processor.process_token(token)
    #         print(f"Term: {term}, Position: {position}")
    #         index.add_term(term=term, position=position, doc_id=d.id)
    #         position += 1
    # return index
    token_processor = NewTokenProcessor()
    # token_processor = BasicTokenProcessor()
    index = PositionalInvertedIndex()
    for d in corpus:
        stream = EnglishTokenStream(d.get_content())
        position = 1
        for token in stream:
            terms = token_processor.process_token(token)
            for term in terms:
                index.add_term(term=term, position=position, doc_id=d.id)
            position += 1
    return index


if __name__ == "__main__":
    corpus_path = Path()
    corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    #corpus_path = Path('all-nps-sites-extracted')
    #corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # Build the index over this directory.
    index = index_corpus(corpus)

    start = time_ns()
    index = index_corpus(corpus)
    end = time_ns()
    print(f"Building Index: {round(end - start, 2)} ns")

    #term = 'york -new'# ---Not query
    #term = 'university'
    #term = '"new york university"' #--- Phrase Literal
    #term = "in + new" # ---And query
    #term = "new + york"  # ---Or query
    #term = 'New York University Ranked Best in New York State'
    #term = 'in new york'
    #term = '"York University Opens New Science Lab"' #--- works doc id = 3

    #term = '"new york university" -in'

    #term = '"new york" -science -debt'

    term = '"new york university ranked best in new"'
    print(f"\nTerm:{term}")



    booleanqueryparser = BooleanQueryParser()
    # parse the given query and print the postings
    querycomponent = booleanqueryparser.parse_query(query=term)
    print("Done with parsing the query, print the output \n")
    postings_result = querycomponent.get_postings(index, NewTokenProcessor())
    for posting in postings_result:
        print("In main.py: ", posting.doc_id)


    # term = "new"
    # print(f"\nTerm:{term}")
    # querycomponent = booleanqueryparser.parse_query(term)
    # for posting in querycomponent.get_postings(index):
    #     print(posting)
    #
    # term = "york"
    # print(f"\nTerm:{term}")
    # querycomponent = booleanqueryparser.parse_query(term)
    # for posting in index.get_postings(term):
    #     print(posting)
    #
    # term = "in"
    # print(f"\nTerm:{term}")
    # querycomponent = booleanqueryparser.parse_query(term)
    # for posting in index.get_postings(term):
    #     print(posting)
    #
