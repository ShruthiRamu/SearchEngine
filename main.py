from itertools import tee
from pathlib import Path
import os
import cardinality
from porter2stemmer import Porter2Stemmer
import SoundexIndexer
from diskindexwriter import DiskIndexWriter
from indexes.diskpositionalindex import DiskPositionalIndex
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.invertedindex import InvertedIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from ranked_strategy import DefaultStrategy, RankedStrategy, TraditionalStrategy, OkapiBM25Strategy, WackyStrategy
from queries import BooleanQueryParser, PhraseLiteral
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor
from typing import List
from numpy import log as ln
from math import sqrt
from heapq import nlargest

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

# def index_corpus(corpus: DocumentCorpus):
#
#     token_processor = NewTokenProcessor()
#     positional_index = PositionalInvertedIndex()
#     biword_index = InvertedIndex()
#
#     for d in corpus:
#         stream = EnglishTokenStream(d.get_content())
#         position = 1
#
#         # Build  index
#         current_terms = []
#         next_terms = []
#         for current, next in pairwise(stream):
#             current_terms = token_processor.process_token(current)
#             next_terms = token_processor.process_token(next)
#             # Build positional index
#             for term in current_terms:
#                 positional_index.add_term(term=term, position=position, doc_id=d.id)
#             for term1, term2 in zip(current_terms, next_terms):
#                 # concatenate the pair as a single term
#                 biword_term = term1 + ' ' + term2
#                 # Build biword index
#                 biword_index.add_term(term=biword_term, doc_id=d.id)
#             position += 1
#         # Adding the final term
#         for term in next_terms:
#             positional_index.add_term(term=term, position=position, doc_id=d.id)
#     return positional_index, biword_index
#
#
# def pairwise(iterable):
#     # "s -> (s0,s1), (s1,s2), (s2, s3), ..."
#     a, b = tee(iterable)
#     next(b, None)
#     return zip(a, b)


# def index_corpus(corpus: DocumentCorpus) -> (Index, List[float], List[int], int, float, float):
#     token_processor = NewTokenProcessor()
#     index = PositionalInvertedIndex()
#     document_weights = []  # Ld for all documents in corpus
#     document_tokens_length_per_document = []  # docLengthd - Number of tokens in a document
#     document_tokens_length_total = 0  # total number of tokens in all the documents in corpus
#     average_tftds = []  # ave(tftd) - average tftd count for a particular document
#     byte_size_ds = []  # byteSized - number of bytes in the file for document d
#     for d in corpus:
#         # print("Processing the document: ", d)
#         term_tftd = {}  # Term -> Term Frequency in a document
#         stream = EnglishTokenStream(d.get_content())
#         document_tokens_length_d = 0  # docLengthd - number of tokens in the document d
#         position = 1
#         for token in stream:
#             terms = token_processor.process_token(token)
#             for term in terms:
#                 if term not in term_tftd.keys():
#                     term_tftd[term] = 0  # Initialization
#                 term_tftd[term] += 1
#                 # TODO: Add biword index
#                 index.add_term(term=term, position=position, doc_id=d.id)
#             position += 1
#             # number of tokens in document d
#             document_tokens_length_d += 1
#
#         Ld = 0
#         for tftd in term_tftd.values():
#             wdt = 1 + ln(tftd)
#             wdt = wdt ** 2
#             Ld += wdt
#         Ld = sqrt(Ld)
#         document_weights.append(Ld)
#         # docLengthd - update the number of tokens for the document
#         document_tokens_length_per_document.append(document_tokens_length_d)
#         # update the sum of tokens in all documents
#         document_tokens_length_total = document_tokens_length_total + document_tokens_length_d
#
#         # ave(tftd) - average tftd count for a particular document
#         total_tftd = 0
#         average_tftd = 0
#         for tf in term_tftd.values():
#             total_tftd += tf
#         # print("Total tftd and len(term_tftf) for doc d: ", d.get_file_name(), total_tftd, len(term_tftd))
#         # Handling empty files
#         if total_tftd == 0 or len(term_tftd) == 0:
#             average_tftds.append(average_tftd)
#         else:
#             average_tftd = total_tftd / len(term_tftd)
#             average_tftds.append(average_tftd)
#
#         # byteSized - number of bytes in the file for document d
#         # TODO: Fix this to get the correct number of bytes
#         byte_size_d = d.get_file_size()
#         byte_size_ds.append(byte_size_d)
#
#     # docLengthA - average number of tokens in all documents in the corpus
#     document_tokens_length_average = document_tokens_length_total / len(corpus)
#     return index, document_weights, document_tokens_length_per_document, byte_size_ds, average_tftds, document_tokens_length_average

def pairwise(iterable):
    # "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = tee(iterable)
    next(b, None)
    return zip(a, b)


def index_corpus(corpus: DocumentCorpus) -> (Index, List[float], List[int], int, float, float):
    token_processor = NewTokenProcessor()
    index = PositionalInvertedIndex()
    biword_index = InvertedIndex()
    document_weights = []  # Ld for all documents in corpus
    document_tokens_length_per_document = []  # docLengthd - Number of tokens in a document
    document_tokens_length_total = 0  # total number of tokens in all the documents in corpus
    average_tftds = []  # ave(tftd) - average tftd count for a particular document
    byte_size_ds = []  # byteSized - number of bytes in the file for document d
    for d in corpus:
        # print("Processing the document: ", d)
        term_tftd = {}  # Term -> Term Frequency in a document
        stream = EnglishTokenStream(d.get_content())
        document_tokens_length_d = 0  # docLengthd - number of tokens in the document d
        position = 1
        # Start processing the tokens
        current_terms = []
        next_terms = []
        for current, next in pairwise(stream):
            current_terms = token_processor.process_token(current)
            next_terms = token_processor.process_token(next)
            # Build positional index
            for term in current_terms:
                if term not in term_tftd.keys():
                    term_tftd[term] = 0  # Initialization
                term_tftd[term] += 1
                index.add_term(term=term, position=position, doc_id=d.id)
            for term1, term2 in zip(current_terms, next_terms):
                # concatenate the pair as a single term
                biword_term = term1 + ' ' + term2
                # Build biword index
                biword_index.add_term(term=biword_term, doc_id=d.id)
            position += 1
            # number of tokens in document d
            document_tokens_length_d += 1

        # Adding the final term
        for term in next_terms:
            if term not in term_tftd.keys():
                term_tftd[term] = 0  # Initialization
            term_tftd[term] += 1
            index.add_term(term=term, position=position, doc_id=d.id)
        document_tokens_length_d += 1

        Ld = 0
        for tftd in term_tftd.values():
            wdt = 1 + ln(tftd)
            wdt = wdt ** 2
            Ld += wdt
        Ld = sqrt(Ld)
        document_weights.append(Ld)
        # docLengthd - update the number of tokens for the document
        document_tokens_length_per_document.append(document_tokens_length_d)
        # update the sum of tokens in all documents
        document_tokens_length_total = document_tokens_length_total + document_tokens_length_d

        # ave(tftd) - average tftd count for a particular document
        total_tftd = 0
        average_tftd = 0
        for tf in term_tftd.values():
            total_tftd += tf
        # print("Total tftd and len(term_tftf) for doc d: ", d.get_file_name(), total_tftd, len(term_tftd))
        # Handling empty files
        if total_tftd == 0 or len(term_tftd) == 0:
            average_tftds.append(average_tftd)
        else:
            average_tftd = total_tftd / len(term_tftd)
            average_tftds.append(average_tftd)

        # byteSized - number of bytes in the file for document d
        byte_size_d = d.get_file_size()
        byte_size_ds.append(byte_size_d)

    # docLengthA - average number of tokens in all documents in the corpus
    document_tokens_length_average = document_tokens_length_total / len(corpus)
    return index, biword_index, document_weights, document_tokens_length_per_document, byte_size_ds, average_tftds, document_tokens_length_average


" Main Application of Search Engine "

if __name__ == "__main__":

    # Building Soundex Index
    # print("Soundex Indexing...")
    # soundex_indexer_dir = 'mlb-articles-4000'
    # corpus_path = Path(soundex_indexer_dir)
    # soundex_corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    # start = time_ns()
    # i_index, soundex_index = SoundexIndexer.index_corpus(soundex_corpus)
    # end = time_ns()
    # print(f"Soundex Indexing Time: {(end - start)/1e+9} secs\n")

    # RANKING STRATEGY
    strategyMap = {1: DefaultStrategy, 2: TraditionalStrategy, 3: OkapiBM25Strategy, 4: WackyStrategy}

    mode_selection_instr = "[1] Build Index \n[2] Query Index \n>> "
    mode = input(mode_selection_instr)

    querying_style_selected = False
    ranking_startegy_selected = False

    initial_indexing = True if int(mode) == 1 else False
    querying_mode = not initial_indexing
    empty_query = True

    while True:
        # Start building index or querying
        if initial_indexing:
            print("Initial Indexing mode...")
            query = ""

        if querying_mode:
            if empty_query:
                query = ""
            else:
                print("\nSearch")
                query = input(">> ")

        #  index the specified folder
        if query.startswith(":index") or empty_query or initial_indexing:
            while True:
                # Assuming in cwd
                dir = input("Enter Directory Name: ") if initial_indexing or querying_mode else query
                if initial_indexing or querying_mode or dir.startswith(":index"):
                    if dir.startswith(":index"):
                        _, dir = dir.split(" ")
                    corpus_path = Path(dir.rstrip())
                    if corpus_path.is_dir():
                        if any(f.endswith('.txt') for f in os.listdir(corpus_path)):
                            corpus = DirectoryCorpus.load_text_directory(corpus_path, '.txt')
                            corpus_size = len(list(corpus_path.glob("*.txt")))
                        elif any(f.endswith('.json') for f in os.listdir(corpus_path)):
                            corpus = DirectoryCorpus.load_json_directory(corpus_path, '.json')
                            corpus_size = len(list(corpus_path.glob("*.json")))
                        break
                    else:
                        print("Directory doesn't exist\n")

            index_path = corpus_path / "index"
            index_path = index_path.resolve()

            biword_index_path = corpus_path / "biword_index"
            biword_index_path = biword_index_path.resolve()

            print("Indexing...")
            start = time_ns()
            positional_index, biword_index, document_weights, document_tokens_length_per_document, byte_size_d, average_tftd, document_tokens_length_average \
                = index_corpus(corpus)
            end = time_ns()
            print(f"In-Memory Indexing Time: {(end - start) / 1e+9} secs\n")

            # TODO: REMOVE AFTER CREATING A VOCAB LIST
            vocab_list_path = index_path / "vocab_list.txt"
            with open(vocab_list_path, 'w') as f:
                f.writelines('\n'.join(vocab))

            # Creates a new folder inside corpus to store on-disk index information
            if not index_path.is_dir():
                index_path.mkdir()
                index_writer = DiskIndexWriter(index_path, document_weights, document_tokens_length_per_document,
                                               byte_size_d, average_tftd, document_tokens_length_average)
                # Write Positional Inverted Index to disk
                index_writer.write_index(positional_index)

            # Creates a new folder inside corpus to store on-disk biword-index information
            if not biword_index_path.is_dir():
                biword_index_path.mkdir()
                biword_index_writer = DiskIndexWriter(biword_index_path)
                # Write Biword Index to disk
                biword_index_writer.write_index(biword_index)

            if initial_indexing:
                print("\nQutting the program...")
                quit()

            if empty_query:
                index_writer = DiskIndexWriter(index_path)
                biword_index_writer = DiskIndexWriter(biword_index_path)
                empty_query = False

            disk_index = DiskPositionalIndex(index_writer)
            biword_disk_index = DiskPositionalIndex(biword_index_writer)

        elif query == ":q":
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
            vocabulary = disk_index.vocabulary()
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
                    print("-" * 50)
                    print(f"Author: {author_name.capitalize()}")
                    for i, posting in enumerate(postings):
                        print(f"[{i + 1}] {soundex_corpus.get_document(posting.doc_id).title}")
            else:
                print("No author matches found")

        elif query.startswith(":querystyle"):
            print("\nQuery Style:")
            query_style = input("[1] Boolean \n[2] Ranked \n>> ")
            querying_style_selected = True

        elif query.startswith(":rankformula"):
            print("\nChoose a ranking strategy:")
            print("1. Default")
            print("2. Traditional(tf-idf)")
            print("3. Okapi BM25")
            print("4. Wacky")
            choice = input(">> ")
            strategy = strategyMap.get(int(choice))
            ranking_startegy_selected = True

        # Handle and parse the query
        elif querying_mode:
            # TWO QUERYING SYTLES: BOOLEAN & RANKED
            if not querying_style_selected:
                print("\nQuery Style:")
                query_style = input("[1] Boolean \n[2] Ranked \n>> ")
                querying_style_selected = True

            if int(query_style) == 1:
                # BOOLEAN QUERIES
                token_processor = NewTokenProcessor()
                print(f"\nSearching the Term:{query}")
                booleanqueryparser = BooleanQueryParser()

                # parse the given query and print the postings
                querycomponent = booleanqueryparser.parse_query(query=query)

                # Handle if it is a biword phrase query
                if isinstance(querycomponent, PhraseLiteral) and len(querycomponent.terms) == 2:
                    print("Found biword phrase query hence using biword on disk index.....\n")
                    postings = querycomponent.get_postings(biword_disk_index, NewTokenProcessor())
                else:
                    # Quickfix done: Breaks for "law prohibit" -camping, because phrase literal thinks its biword index
                    postings = querycomponent.get_postings(disk_index, NewTokenProcessor())
                # Get all the doc ids
                doc_ids = [p.doc_id for p in postings]
                doc_ids = list(set(doc_ids))
                num_docs = len(doc_ids)

                for i, doc_id in enumerate(doc_ids):
                    print(f"[{i + 1}] {corpus.get_document(doc_id).title}")
                print(f"Total Documents: {num_docs}")

                if num_docs:
                    print("\nEnter Document Number(or 0) to view(or skip) content:")
                    while True:
                        doc_num = int(input("Doc No: "))
                        if 0 < doc_num <= num_docs:
                            print(f"Document {doc_num} Content:")
                            doc_content = corpus.get_document(doc_ids[doc_num - 1]).get_content()
                            for c in doc_content:
                                print(c)
                            break
                        elif doc_num:
                            print("Enter a valid document number")
                        else:
                            break  # Skip the viewing of content


            else:
                # RANKED RETRIEVAL MODE
                if not ranking_startegy_selected:
                    print("\nChoose a ranking strategy:")
                    print("1. Default")
                    print("2. Traditional(tf-idf)")
                    print("3. Okapi BM25")
                    print("4. Wacky")
                    choice = input(">> ")
                    strategy = strategyMap.get(int(choice))
                    ranking_startegy_selected = True

                rankedStrategy = RankedStrategy(strategy)

                # PERFORM RANKED RETRIEVAL ALGORITHM
                print(f"Query going in: {query}")
                accumulator = rankedStrategy.calculate(query, disk_index, corpus_size)

                # SHOW THE RESULTS
                K = 10
                heap = [(score, doc_id) for doc_id, score in accumulator.items()]
                print("*" * 80)
                print(f"Top {K} documents for query: {query}")
                for k_documents in nlargest(K, heap):
                    score, doc_id = k_documents
                    print(f"Doc Title: {corpus.get_document(doc_id).title}, Score: {score}")
