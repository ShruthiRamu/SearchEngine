from itertools import tee
from pathlib import Path
import os
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

        # Build  index
        current_terms = []
        next_terms = []
        for current, next in pairwise(stream):
            current_terms = token_processor.process_token(current)
            next_terms = token_processor.process_token(next)
            # Build positional index
            for term in current_terms:
                positional_index.add_term(term=term, position=position, doc_id=d.id)
            for term1, term2 in zip(current_terms, next_terms):
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

    # Building Soundex Index
    print("Soundex Indexing...")
    soundex_indexer_dir = 'mlb-articles-4000'
    corpus_path = Path(soundex_indexer_dir)
    soundex_corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    start = time_ns()
    i_index, soundex_index = SoundexIndexer.index_corpus(soundex_corpus)
    end = time_ns()
    print(f"Soundex Indexing Time: {(end - start)/1e+9} secs\n")

    program_start = True
    while True:
        query = "" if program_start else input("\nEnter Search Query: ")
        #  index the specified folder
        if program_start or query.startswith(":index"):
            while True:
                # Assuming in cwd
                dir = input("Enter Directory Name: ") if program_start else query
                if program_start or dir.startswith(":index"):
                    if dir.startswith(":index"):
                        _, dir = dir.split(" ")
                    corpus_path = Path(dir.rstrip())
                    if corpus_path.is_dir():
                        if any(f.endswith('.txt') for f in os.listdir(corpus_path)):
                            corpus = DirectoryCorpus.load_text_directory(corpus_path, '.txt')
                        elif any(f.endswith('.json') for f in os.listdir(corpus_path)):
                            corpus = DirectoryCorpus.load_json_directory(corpus_path, '.json')
                        break
                    else:
                        print("Directory doesn't exist\n")

            print("Indexing...")
            program_start = False
            start = time_ns()
            positional_index, biword_index = index_corpus(corpus)
            end = time_ns()
            print(f"Positional & Biword Indexing Time: {(end - start)/1e+9} secs\n")

        elif query.startswith(":q"):
            print("Quitting the program....")
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
            authors = SoundexIndexer.soundex_indexer(query=author, index=i_index,
                                           soundex_index=soundex_index)
            if authors:
                for author in authors:
                    postings = i_index.get_postings(author)
                    print(f"Author: {author.capitalize()}, Total Documents Found: {len(postings)}")

                author_name = input("Enter author name(or 'type skip') from database to view title:")
                if author_name != 'skip':
                    postings = i_index.get_postings(author_name)
                    print("-"*50)
                    print(f"Author: {author_name.capitalize()}")
                    for i, posting in enumerate(postings):
                        print(f"[{i + 1}] {soundex_corpus.get_document(posting.doc_id).title}")
            else:
                print("No author matches found")


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
            num_docs = len(doc_ids)

            for i, doc_id in enumerate(doc_ids):
                print(f"[{i+1}] {corpus.get_document(doc_id).title}")
            print(f"Total Documents: {num_docs}")

            if num_docs:
                print("\nEnter Document Number(or 0) to view(or skip) content:")
                while True:
                    doc_num = int(input("Doc No: "))
                    if 0 < doc_num <= num_docs:
                        print(f"Document {doc_num} Content:")
                        doc_content = corpus.get_document(doc_ids[doc_num-1]).get_content()
                        for c in doc_content:
                            print(c)
                        break
                    elif doc_num:
                        print("Enter a valid document number")
                    else:
                        break # Skip the viewing of content
