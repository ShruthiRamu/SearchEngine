import os.path
from itertools import tee
from pathlib import Path
from diskindexwriter import DiskIndexWriter
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.diskpositionalindex import DiskPositionalIndex
from indexes.invertedindex import InvertedIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser, PhraseLiteral
from ranked_strategy import DefaultStrategy, RankedStrategy, TraditionalStrategy, OkapiBM25Strategy, WackyStrategy
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor
from numpy import log as ln
from math import sqrt
from typing import List
from struct import pack, unpack
from heapq import nlargest


def index_corpus(corpus: DocumentCorpus) -> (Index, List[float], List[int], int, float, float):
    print("Indexing..")
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
        # for token in stream:
        #     terms = token_processor.process_token(token)
        #     for term in terms:
        #         if term not in term_tftd.keys():
        #             term_tftd[term] = 0  # Initialization
        #         term_tftd[term] += 1
        #         # TODO: Add biword index
        #         index.add_term(term=term, position=position, doc_id=d.id)
        #     position += 1
        #     # number of tokens in document d
        #     document_tokens_length_d += 1
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
                # print("Biword term: ", biword_term)
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


# def index_corpus(corpus: DocumentCorpus) -> (Index, List[float], List[int], int, float, float):
#     print("Indexing..")
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


" Main Application of Search Engine "

if __name__ == "__main__":

    # corpus_path = Path("dummyjsonfiles")
    # corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    corpus_path = Path("all-nps-sites-extracted")
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # index, document_weights, document_tokens_length_per_document, byte_size_d, average_tftd, \
    # document_tokens_length_average = index_corpus(corpus)

    index, biword_index, document_weights, document_tokens_length_per_document, byte_size_d, average_tftd, \
    document_tokens_length_average = index_corpus(corpus)

    index_path = corpus_path / "index"
    index_path = index_path.resolve()
    if not index_path.is_dir():
        index_path.mkdir()

    # Create a directory for biword index on disk
    biword_index_path = corpus_path / "biword_index"
    biword_index_path = biword_index_path.resolve()
    if not biword_index_path.is_dir():
        biword_index_path.mkdir()

    # corpus_size = len(document_weights)
    corpus_size = len(list(corpus_path.glob("*.json")))

    # BOOLEAN QUERIES

    index_writer = DiskIndexWriter(index_path=index_path)

    # Prepare biword index
    biword_index_writer = DiskIndexWriter(index_path=biword_index_path)

    # Write Disk Positional Inverted Index once
    if not index_writer.posting_path.is_file():
        index_writer.write_index(index)

    # Write Disk Biword Index once
    if not biword_index_writer.posting_path.is_file():
        biword_index_writer.write_index(biword_index)

    # query = '"national park"'
    # query = '"Carver Birthplace Association"'
    # query = '"Coral Reef"'
    # query = '"new bedford whaling national historical park"'
    # query = '"museum fees"'
    # query = '[Coral NEAR/4 Products]'
    query = '[learn NEAR/3 park]'
    token_processor = NewTokenProcessor()
    print(f"\nSearching the Term:{query}")
    booleanqueryparser = BooleanQueryParser()

    # parse the given query and print the postings
    querycomponent = booleanqueryparser.parse_query(query=query)

    # Handle if it is a biword phrase query
    if isinstance(querycomponent, PhraseLiteral) and len(querycomponent.terms) == 2:
        print("Found biword phrase query hence using biword index.....\n")
        biword_disk_index = DiskPositionalIndex(biword_index_writer)
        postings = querycomponent.get_postings(biword_disk_index, NewTokenProcessor())
    else:
        disk_index = DiskPositionalIndex(index_writer)
        postings = querycomponent.get_postings(disk_index, NewTokenProcessor())

    # Get all the doc ids
    doc_ids = [p.doc_id for p in postings]
    doc_ids = list(set(doc_ids))
    num_docs = len(doc_ids)
    print(f"Total Documents: {num_docs}")

    for i, doc_id in enumerate(doc_ids):
        print(f"[{i + 1}] {corpus.get_document(doc_id).title}, {corpus.get_document(doc_id).get_file_name()}")
    print(f"Total Documents: {num_docs}")

    # RANKED RETRIEVAL

    # index_writer = DiskIndexWriter(index_path, document_weights, document_tokens_length_per_document,
    #                                byte_size_d, average_tftd, document_tokens_length_average)
    #
    # # Write Disk Positional Inverted Index once
    # if not index_writer.posting_path.is_file():
    #     index_writer.write_index(index)
    #
    # strategyMap = {1: DefaultStrategy, 2: TraditionalStrategy, 3: OkapiBM25Strategy, 4: WackyStrategy}
    #
    # while True:
    #     print("Choose a ranking strategy\n")
    #     print("1. Default\n")
    #     print("2. Traditional(tf-idf)\n")
    #     print("3. Okapi BM25\n")
    #     print("4. Wacky\n")
    #     print("5. Exit")
    #
    #     choice = input()
    #     if int(choice) == 5:
    #         print("Exiting the program...")
    #         exit(0)
    #
    #     strategy = strategyMap.get(int(choice))
    #     rankedStrategy = RankedStrategy(strategy)
    #
    #     # query = "new york univers"
    #     # query = "Coral Reef"
    #     # query = "camping in yosemite"
    #     # query = "strenuous"
    #     query = "devils postpile"
    #
    #     disk_index = DiskPositionalIndex(index_writer)
    #
    #     accumulator = rankedStrategy.calculate(query, disk_index, corpus_size)
    #
    #     # print("Returned value: ", accumulator)
    #
    #     K = 10
    #     heap = [(score, doc_id) for doc_id, score in accumulator.items()]
    #     print(f"Top {K} documents for query: {query}")
    #     for k_documents in nlargest(K, heap):
    #         score, doc_id = k_documents
    #         print(f"Doc Title: {corpus.get_document(doc_id).title}, Score: {score}")
    #         # print(f"Doc id: {doc_id}, Score: {score}")
