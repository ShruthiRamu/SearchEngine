from pathlib import Path

from porter2stemmer import Porter2Stemmer
import SoundexIndexer
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor

mapping = {}


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = NewTokenProcessor()
    # token_processor = BasicTokenProcessor()
    index = PositionalInvertedIndex()
    for d in corpus:
        mapping[d.id] = d.id
        stream = EnglishTokenStream(d.get_content())
        position = 1
        for token in stream:
            terms = token_processor.process_token(token)
            for term in terms:
                index.add_term(term=term, position=position, doc_id=d.id)
            position += 1
    return index


" Main Application of Search Engine "
import numpy as np

if __name__ == "__main__":
    #neal_file = open("Neal_files.txt", "r")
    #neal_files = np.array([new_file.rstrip() for new_file in neal_file.readlines()], dtype=object)
    #ourfiles = []

    # Assuming in cwd
    # dir = input("Enter Directory Name: ")
    # Construct a path
    corpus_path = Path('all-nps-sites-extracted')

    #corpus_path = Path('dummy')
    #print(corpus_path)
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    start = time_ns()
    index = index_corpus(corpus)
    end = time_ns()
    print(f"Building Index: {round(end-start, 2)} ns")

    soundex_indexer_dir = 'mlb-articles-4000'
    corpus_path = Path(soundex_indexer_dir)
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    start = time_ns()
    i_index, soundex_index = SoundexIndexer.index_corpus(corpus)
    end = time_ns()
    print(f"Building  Soundex Index: {round(end - start, 2)} ns")

    # This is for debugging

    # print("Postings for camp: ", index.get_positional_postings("camp"))
    # print("Postings for camp: ", index.get_positional_postings("camping"))
    # for posting in index.get_positional_postings("camp"):
    #     print(posting)
    # print("Vocab for 2.json: ", index.vocabulary())
    #
    # print("BooleanQueryParser.....")
    # token_processor = NewTokenProcessor()
    # booleanqueryparser = BooleanQueryParser()
    # # parse the given query and print the postings
    # querycomponent = booleanqueryparser.parse_query(query='including the')
    #
    # postings = querycomponent.get_positional_postings(index, token_processor=token_processor)
    # for post in postings:
    #     print(post)
    #
    # quit()

    while True:
        query = input("\nEnter Search Query: ")

        if query.startswith(":q"):
            print("\nQuitting the program....")
            break

        # print the stemmed term
        # TODO: Handle when string with space is provided
        elif query.startswith(":stem"):
            token = query.split(" ")[1]
            if not token:
                print("No token entered")
                continue
            stemmer = Porter2Stemmer()
            stemmed_term = stemmer.stem(token)
            print("\nStemmed term: ", stemmed_term)

        #  index the specified folder
        elif query.startswith(":index"):
            directory_name = query.split(" ")[1]
            if not directory_name:
                print("No directory name specified")
                continue
            corpus_path = Path(directory_name)
            corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
            index = index_corpus(corpus)

        #  print the vocabulary
        elif query.startswith(":vocab"):
            # Print 1000 terms in vocabulary
            vocabulary = index.vocabulary()
            vocabulary_length = len(vocabulary)
            if vocabulary_length:
                vocab = vocabulary[:1000]
                print("First 1000(less) terms in vocabulary(sorted): ")
                print(*vocab, sep="\n")
                print("Total number of vocabulary terms: ", vocabulary_length)
            else:
                print("No vocabulary found")

        # print the documents that matches the provided author
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
            if len(query.split(" ")) == 2:
                # Use the biword index
                pass
            else:
                # Use the positional index
                pass

            print(f"\nSearching the Term:{query}")
            booleanqueryparser = BooleanQueryParser()
            # parse the given query and print the postings
            querycomponent = booleanqueryparser.parse_query(query=query)

            postings = querycomponent.get_postings(index, token_processor=token_processor)
            for posting in postings:
                print(posting)
                # ourfiles.append(mapping[posting.doc_id])

            # For debugging
            # print("\nNeal Files: ")
            # ourfiles = np.array(ourfiles, dtype=object)
            # print(neal_files[np.where(neal_files != ourfiles)[0]])

            print(f"Total Documents: {len(postings)}")