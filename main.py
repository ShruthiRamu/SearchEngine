from pathlib import Path

from porter2stemmer import Porter2Stemmer
from SoundexIndexer import soundex_indexer
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor

def index_corpus(corpus: DocumentCorpus) -> Index:
    #token_processor = NewTokenProcessor()
    token_processor = BasicTokenProcessor()
    index = PositionalInvertedIndex()
    for d in corpus:
        stream = EnglishTokenStream(d.get_content())
        position = 1
        for token in stream:
            term = token_processor.process_token(token)
            # for term in terms:
            index.add_term(term=term, position=position, doc_id=d.id)
            position += 1
    return index

" Main Application of Search Engine "

if __name__ == "__main__":

    # Assuming in cwd
    # dir = input("Enter Directory Name: ")
    # Construct a path
    corpus_path = Path('all-nps-sites-extracted')
    #corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    start = time_ns()
    index = index_corpus(corpus)
    end = time_ns()
    print(f"Building Index: {round(end-start, 2)} ns")

    while True:
        query = input("\nEnter Search Query: ")

        if query.startswith(":q"):
            print("\nQuitting the program....")
            break

        # print the stemmed term
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
            soundex_indexer(query=author) # INDEXING: Time Consuming

        # Handle and parse the query
        else:
            term = query
            print(f"\nSearching the Term:{query}")
            booleanqueryparser = BooleanQueryParser()
            # parse the given query and print the postings
            querycomponent = booleanqueryparser.parse_query(query=term)

            postings = querycomponent.get_postings(index)
            for posting in postings:
                print(posting)
            print(f"Total Documents: {len(postings)}")
