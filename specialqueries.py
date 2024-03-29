import re
from pathlib import Path

from porter2stemmer import Porter2Stemmer

from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

"""This basic program builds a positional indexes and boolean queries over the files in 
the directory provided"""


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
    #  Initially index the current directory
    corpus_path = Path()
    corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(corpus)

    # test_query = ":index utf_corpus"
    # if re.match(special_queries_pattern, test_query): # can also use re.search(), but re.match only checks the beginning
    #     query = test_query.partition(":")[2] # fetch the string after :
    #     print(query)
    # else:
    #     query = test_query

    while True:
        print("Enter a search query/ Enter 'quit' to exit: ")
        query = input()

        # Remove leading spaces
        query = query.lstrip()
        print("query entered: ", query)

        # special_queries_pattern = '^:'
        # re.match(special_queries_pattern, query):
        #  special_query_string = query.partition(":")[2]  # Get the special query and the arguments
        #  print("special query entered: ", special_query_string)

        # Check if special query

        # quit the program
        if query.startswith(":q") or query == 'quit':
            print("Quitting the program....")
            exit(0)
        # print stemmed term
        elif query.startswith(":stem"):
            token = query.split(" ")[1]
            if not token:
                print("No token entered")
                continue
            stemmer = Porter2Stemmer()
            stemmed_term = stemmer.stem(token)
            print("Stemmed term: ", stemmed_term)
        #  index the specified folder
        elif query.startswith(":index"):
            directory_name = query.split(" ")[1]
            if not directory_name:
                print("No directory name specified")
                continue
            corpus_path = Path(directory_name)
            corpus = DirectoryCorpus.load_text_directory(corpus_path.absolute(), ".txt")
            # For now this will be just json files
            # Build the index over this directory.
            index = index_corpus(corpus)
            continue
        #  print the vocabulary
        elif query.startswith(":vocab"):
            # Milestone 1 says to print 1000 terms in vocabulary of corpus. Is the corpus json files?
            vocab = index.vocabulary()[:1000]
            if len(vocab) == 0 or vocab is None:
                print("No vocabulary found")
                continue
            print("First 1000(less) terms in vocabulary(sorted): ")
            print(*vocab, sep="\n")
            print("Total number of vocabulary terms: ", len(index.vocabulary()))

        # print the documents that matches the provided author
        elif query.startswith(":author"):
            hash_term = query.split(" ")[1]
            if not hash_term:
                print("No author specified")
                continue
            # TODO: Update and call to get the postings. Display the documents from that author
            print("Author: ")
            print("Documents matching the author: ")

        # parse the query
        else:
            term = query
            print(f"\nSearching the Term:{query}")

            booleanqueryparser = BooleanQueryParser()
            # parse the given query and print the postings
            querycomponent = booleanqueryparser.parse_query(query=term)
            for posting in querycomponent.get_postings(index):
                print(posting)
