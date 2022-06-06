from itertools import tee
from pathlib import Path
from time import time_ns

from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.invertedindex import InvertedIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser, PhraseLiteral
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream
from text.newtokenprocessor import NewTokenProcessor

"""This basic program builds a positional inverted index over the .txt files in 
the same directory as this file."""


def index_corpus(corpus: DocumentCorpus):
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
    positional_index = PositionalInvertedIndex()
    biword_index = InvertedIndex()
    for d in corpus:
        print("Going through the document: ", d.title)
        stream = EnglishTokenStream(d.get_content())
        position = 1
        # for token in stream:
        #     terms = token_processor.process_token(token)
        #     for term in terms:
        #         index.add_term(term=term, position=position, doc_id=d.id)
        #     position += 1

        # TODO: Losing the last few documents because of pairwise, fix this
        # Build  index
        current_terms = []
        next_terms = []
        for current, next in pairwise(stream):
            current_terms = token_processor.process_token(current)
            next_terms = token_processor.process_token(next)
            for term in current_terms:
                print("Adding term to positional index: ", term)
                positional_index.add_term(term=term, position=position, doc_id=d.id)
            for term1, term2 in zip(current_terms, next_terms):
                # Build positional index print("Adding term to positional index: ", term1) positional_index.add_term(
                # term=term1, position=position, doc_id=d.id)
                # TODO: Confirm if & gets converted to blank white space/empty??
                #  for " about the-park photo", token provides thepark, the, park.Biword index added to
                #  this is "about thepark" and "thepark photo" concatenate the pair as a single term
                biword_term = term1 + ' ' + term2
                print("Adding term to biword index: ", biword_term)
                # Build biword index
                biword_index.add_term(term=biword_term, doc_id=d.id)
            position += 1
        for term in next_terms:
            print("Adding the last term: ", term)
            positional_index.add_term(term=term, position=position, doc_id=d.id)

    return positional_index, biword_index


def pairwise(iterable):
    # "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


if __name__ == "__main__":
    corpus_path = Path('all-nps-sites-extracted-small')
    # corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # corpus_path = Path('all-nps-sites-extracted')
    # corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # Build the index over this directory.
    start = time_ns()
    positional_index, biword_index = index_corpus(corpus)
    # index = index_corpus(corpus)
    end = time_ns()
    print(f"Building Index: {round(end - start, 2)} ns")

    # term = 'york -new'# ---Not query
    # term = 'university'
    # term = '"new york university"' #--- Phrase Literal
    # term = "in + new" # ---And query
    # term = "new + york"  # ---Or query
    # term = 'New York University Ranked Best in New York State'
    # term = 'in new york'
    # term = '"York University Opens New Science Lab"' #--- works doc id = 3

    # term = '"new york university" -in'

    # term = '"new york" -science -debt'

    # term = '"new york university ranked best in new"'
    # term = '"learn about the Park"'
    # term = ':q park'

    # Learn About the Park
    # term = '[learn NEAR/2 the NEAR/2 photos]' #  1.json and 10.json
    # term = '[signs NEAR/2 be]'  # 4.json
    # term = '[explore NEAR/2 park NEAR/3 involved]'
    term = '[Coral near/4 Products] + "learn about the park"'
    print(f"\nTerm:{term}")

    # print(term.split()[1:])

    booleanqueryparser = BooleanQueryParser()
    # parse the given query and print the postings
    querycomponent = booleanqueryparser.parse_query(query=term)
    print("Done with parsing the query, getting the postings \n")
    # Handle if it is a biword phrase query
    if isinstance(querycomponent, PhraseLiteral) and len(querycomponent.terms) == 2:
        print("Found biword phrase query hence using biword index.....\n")
        postings_result = querycomponent.get_postings(biword_index, NewTokenProcessor())
    else:
        postings_result = querycomponent.get_postings(positional_index, NewTokenProcessor())
    print("Printing doc ids: \n")
    for posting in postings_result:
        print("Doc Ids: ", posting.doc_id)

    print("Printing filenames: \n")
    file_names = [corpus.get_document(posting.doc_id).get_file_name() for posting in postings_result]
    print(file_names)

    print("Printing title: \n")
    titles = [corpus.get_document(posting.doc_id).get_title() for posting in postings_result]
    print(titles)

    # for posting in postings_result:
    #     print(f"Document ID(title) : {corpus.get_document(posting.doc_id).title}")

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
