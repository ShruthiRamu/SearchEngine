from itertools import tee
from pathlib import Path

import cardinality
from porter2stemmer import Porter2Stemmer
import SoundexIndexer
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.invertedindex import InvertedIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser, PhraseLiteral
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor


# def index_corpus(corpus: DocumentCorpus) -> Index:
#     token_processor = NewTokenProcessor()
#     # token_processor = BasicTokenProcessor()
#     index = PositionalInvertedIndex()
#     for d in corpus:
#         stream = EnglishTokenStream(d.get_content())
#         position = 1
#         for token in stream:
#             terms = token_processor.process_token(token)
#             for term in terms:
#                 index.add_term(term=term, position=position, doc_id=d.id)
#             position += 1
#     return index

def index_corpus(corpus: DocumentCorpus):

    token_processor = NewTokenProcessor()

    positional_index = PositionalInvertedIndex()

    biword_index = InvertedIndex()

    for d in corpus:
        stream = EnglishTokenStream(d.get_content())
        position = 1
        # for token in stream:
        #     terms = token_processor.process_token(token)
        #     for term in terms:
        #         index.add_term(term=term, position=position, doc_id=d.id)
        #     position += 1

        # Build  index
        current_terms = []
        next_terms = []
        for current, next in pairwise(stream):
            current_terms = token_processor.process_token(current)
            next_terms = token_processor.process_token(next)
            for term in current_terms:
                positional_index.add_term(term=term, position=position, doc_id=d.id)
            for term1, term2 in zip(current_terms, next_terms):
                # Build positional index
                # print("Adding term to positional index: ", term1)
                # positional_index.add_term(term=term1, position=position, doc_id=d.id)
                # TODO: Confirm if & gets converted to blank white space/empty??
                # TODO: for the-park, token provides thepark, the, park and only biword index added to this is thepark photo
                # concatenate the pair as a single term
                biword_term = term1 + ' ' + term2
                # Build biword index
                biword_index.add_term(term=biword_term, doc_id=d.id)
            position += 1
        # Adding the final term
        for term in next_terms:
            positional_index.add_term(term=term, position=position, doc_id=d.id)
    return positional_index, biword_index


def pairwise(iterable):
    # "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


" Main Application of Search Engine "

if __name__ == "__main__":

    # Assuming in cwd
    # dir = input("Enter Directory Name: ")
    # Construct a path
    corpus_path = Path('all-nps-sites-extracted')

    corpus_nps = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    start = time_ns()
    # index = index_corpus(corpus_nps)
    positional_index, biword_index = index_corpus(corpus_nps)
    end = time_ns()
    print(f"Building Index: {round(end - start, 2)} ns")

    # Building Soundex Index
    soundex_indexer_dir = 'mlb-articles-4000'
    corpus_path = Path(soundex_indexer_dir)
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    start = time_ns()
    i_index, soundex_index = SoundexIndexer.index_corpus(corpus)
    end = time_ns()
    print(f"Building  Soundex Index: {round(end - start, 2)} ns")

    while True:
        query = input("\nEnter Search Query: ")

        if query.startswith(":q"):
            print("\nQuitting the program....")
            break

        # print the stemmed term
        elif query.startswith(":stem"):
            tokens = query.split()[1:]
            if not tokens:
                print("No token entered")
                continue
            stemmer = Porter2Stemmer()
            stemmed_terms = []
            for token in tokens:
                stemmed_terms.append(stemmer.stem(token))
            print("\nStemmed term(s): ", stemmed_terms)

        #  index the specified folder
        elif query.startswith(":index"):
            directory_name = query.split(" ")[1]
            if not directory_name:
                print("No directory name specified")
                continue
            corpus_path = Path(directory_name)
            # TODO: Based on the directory set the file extension and call the load directory accordingly
            corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
            # index = index_corpus(corpus)
            positional_index, biword_index = index_corpus(corpus)

        #  print the vocabulary
        elif query.startswith(":vocab"):
            # Print 1000 terms in vocabulary
            # vocabulary = index.vocabulary()
            vocabulary = positional_index.vocabulary()
            # vocabulary_length = len(vocabulary)
            vocabulary_length = cardinality.count(vocabulary)
            if vocabulary_length:
                vocab = vocabulary[:1000]
                print("First 1000(less) terms in vocabulary(sorted): ")
                print(*vocab, sep="\n")
                print("Total number of vocabulary terms: ", vocabulary_length)
            else:
                print("No vocabulary found")

        # print the documents that match the provided author
        elif query.startswith(":author"):
            author = query.split(" ")[1]
            if not author:
                print("No author specified")
                continue
            SoundexIndexer.soundex_indexer(query=author, index=i_index,
                                           soundex_index=soundex_index)  # INDEXING: Time Consuming

        # Handle and parse the query
        else:
            token_processor = NewTokenProcessor()

            print(f"\nSearching the Term:{query}")
            booleanqueryparser = BooleanQueryParser()

            # parse the given query and print the postings
            querycomponent = booleanqueryparser.parse_query(query=query)

            # Handle if it is a biword phrase query
            if isinstance(querycomponent, PhraseLiteral) and len(querycomponent.terms) == 2:
                print("Found biword phrase query hence using biword index.....\n")
                postings = querycomponent.get_postings(biword_index, NewTokenProcessor())
            else:
                postings = querycomponent.get_postings(positional_index, NewTokenProcessor())
            # Get all the doc ids
            doc_ids = [p.doc_id for p in postings]
            doc_ids = list(set(doc_ids))

            # Get all the file names
            file_names = [corpus_nps.get_document(posting.doc_id).get_file_name() for posting in postings]

            for posting in postings:
                print(f"Document Title : {corpus_nps.get_document(posting.doc_id).title}")

            # print("Printing doc ids: \n")
            # print(doc_ids)

            # print("Printing File names: \n")
            # print(file_names)

            print(f"Total Documents: {len(doc_ids)}")
