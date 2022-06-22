import os.path
from collections import Counter
from functools import reduce
from itertools import tee
from pathlib import Path

import numpy

from diskindexwriter import DiskIndexWriter
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.diskpositionalindex import DiskPositionalIndex
from indexes.invertedindex import InvertedIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser, PhraseLiteral, TermLiteral
from ranked_strategy import DefaultStrategy, RankedStrategy, TraditionalStrategy, OkapiBM25Strategy, WackyStrategy
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor
from numpy import log as ln
from math import sqrt
from typing import List
from struct import pack, unpack
from heapq import nlargest


# def index_corpus(corpus: DocumentCorpus) -> (Index, List[float], List[int], int, float, float):
#     print("Indexing..")
#     token_processor = NewTokenProcessor()
#     index = PositionalInvertedIndex()
#     biword_index = InvertedIndex()
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
#         # for token in stream:
#         #     terms = token_processor.process_token(token)
#         #     for term in terms:
#         #         if term not in term_tftd.keys():
#         #             term_tftd[term] = 0  # Initialization
#         #         term_tftd[term] += 1
#         #         # TODO: Add biword index
#         #         index.add_term(term=term, position=position, doc_id=d.id)
#         #     position += 1
#         #     # number of tokens in document d
#         #     document_tokens_length_d += 1
#         current_terms = []
#         next_terms = []
#         for current, next in pairwise(stream):
#             current_terms = token_processor.process_token(current)
#             next_terms = token_processor.process_token(next)
#             # Build positional index
#             for term in current_terms:
#                 if term not in term_tftd.keys():
#                     term_tftd[term] = 0  # Initialization
#                 term_tftd[term] += 1
#                 index.add_term(term=term, position=position, doc_id=d.id)
#             for term1, term2 in zip(current_terms, next_terms):
#                 # concatenate the pair as a single term
#                 biword_term = term1 + ' ' + term2
#                 # Build biword index
#                 # print("Biword term: ", biword_term)
#                 biword_index.add_term(term=biword_term, doc_id=d.id)
#             position += 1
#             # number of tokens in document d
#             document_tokens_length_d += 1
#
#         # Adding the final term
#         for term in next_terms:
#             if term not in term_tftd.keys():
#                 term_tftd[term] = 0  # Initialization
#             term_tftd[term] += 1
#             index.add_term(term=term, position=position, doc_id=d.id)
#         document_tokens_length_d += 1
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
#     return index, biword_index, document_weights, document_tokens_length_per_document, byte_size_ds, average_tftds, document_tokens_length_average


def index_corpus(corpus: DocumentCorpus) -> (Index, List[float], List[int], int, float, float):
    print("Indexing..")
    token_processor = NewTokenProcessor()
    index = PositionalInvertedIndex()
    document_weights = []  # Ld for all documents in corpus
    document_tokens_length_per_document = []  # docLengthd - Number of tokens in a document
    document_tokens_length_total = 0  # total number of tokens in all the documents in corpus
    average_tftds = []  # ave(tftd) - average tftd count for a particular document
    byte_size_ds = []  # byteSized - number of bytes in the file for document d
    vd_d = {}  # to store the components of centroid vector for each document
    vds = []  # List of list of vds [[vd1],[vd2]]
    for d in corpus:
        # print("Processing the document: ", d)
        term_tftd = {}  # Term -> Term Frequency in a document
        stream = EnglishTokenStream(d.get_content())
        document_tokens_length_d = 0  # docLengthd - number of tokens in the document d
        position = 1
        for token in stream:
            terms = token_processor.process_token(token)
            for term in terms:
                if term not in term_tftd.keys():
                    term_tftd[term] = 0  # Initialization
                term_tftd[term] += 1
                index.add_term(term=term, position=position, doc_id=d.id)
            position += 1
            # number of tokens in document d
            document_tokens_length_d += 1

        Ld = 0
        for t, tftd in zip(term_tftd.keys(), term_tftd.values()):
            wdt = 1 + ln(tftd)
            # Update the component of the vector as wdt
            vd_d[t] = wdt
            wdt = wdt ** 2
            Ld += wdt
        Ld = sqrt(Ld)

        # find v(d)- normalized vector for the document
        for t, tftd in zip(term_tftd.keys(), term_tftd.values()):
            vd_d[t] = vd_d[t] / Ld
            #print("Term: , v(d): ", t, vd_d.get(t))
        print("For a document the VD: ", vd_d)
        vds.append(vd_d)
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
    # calculate centroid
    print("Length of this corpus: ", len(corpus))
    # for vd in vds:
    #     print("vd: ", vd, "\n")
    sorted_vds = []
    for vd in vds:
        s = {k: vd[k] for k in sorted(vd)}
        sorted_vds.append(s)
    # for vd in sorted_vds:
    #     print("vd: ", vd, "\n")

    # Add all the v(d) values of each document for a term
    result = dict(reduce(lambda x, y: Counter(x) + Counter(y), sorted_vds))
    #print("After adding values: ", result)
    Dc = len(corpus)

    # Divide by the Dc - the total number of documents in the corpus
    for i in result:
        result[i] = result[i]/Dc

    print("Final centroid: ", result)
    return index, document_weights, document_tokens_length_per_document, byte_size_ds, average_tftds, document_tokens_length_average


# def pairwise(iterable):
#     # "s -> (s0,s1), (s1,s2), (s2, s3), ..."
#     a, b = tee(iterable)
#     next(b, None)
#     return zip(a, b)


" Main Application of Search Engine "

if __name__ == "__main__":

    # corpus_path = Path("dummyjsonfiles")
    # corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # corpus_path = Path("all-nps-sites-extracted")
    # corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # hamilton_corpus_path = Path("federalist-papers/HAMILTON")
    # hamilton_corpus = DirectoryCorpus.load_text_directory(hamilton_corpus_path, ".txt")
    # hamilton_index, hamilton_document_weights, hamilton_document_tokens_length_per_document, hamilton_byte_size_d, hamilton_average_tftd, \
    # hamilton_document_tokens_length_average = index_corpus(hamilton_corpus)

    # jay_corpus_path = Path("federalist-papers/JAY")
    # jay_corpus = DirectoryCorpus.load_text_directory(jay_corpus_path, ".txt")
    # jay_index, jay_document_weights, jay_document_tokens_length_per_document, jay_byte_size_d, jay_average_tftd, \
    # jay_document_tokens_length_average = index_corpus(jay_corpus)

    madison_corpus_path = Path("federalist-papers/MADISON")
    madison_corpus = DirectoryCorpus.load_text_directory(madison_corpus_path, ".txt")
    madison_index, madison_document_weights, madison_document_tokens_length_per_document, madison_byte_size_d, madison_average_tftd, \
    madison_document_tokens_length_average = index_corpus(madison_corpus)

    # index, document_weights, document_tokens_length_per_document, byte_size_d, average_tftd, \
    # document_tokens_length_average = index_corpus(corpus)

    # index, biword_index, document_weights, document_tokens_length_per_document, byte_size_d, average_tftd, \
    # document_tokens_length_average = index_corpus(corpus)

    # hamilton_index_path = hamilton_corpus_path / "index"
    # hamilton_index_path = hamilton_index_path.resolve()
    # if not hamilton_index_path.is_dir():
    #     hamilton_index_path.mkdir()
    #
    # jay_index_path = jay_corpus_path / "index"
    # jay_index_path = jay_index_path.resolve()
    # if not jay_index_path.is_dir():
    #     jay_index_path.mkdir()
    #
    # madison_index_path = madison_corpus_path / "index"
    # madison_index_path = madison_index_path.resolve()
    # if not madison_index_path.is_dir():
    #     madison_index_path.mkdir()
    #
    # # corpus_size = len(document_weights)
    # # corpus_size = len(list(corpus_path.glob("*.json")))
    #
    # hamilton_corpus_size = len(list(hamilton_corpus_path.glob("*.txt")))
    # jay_corpus_size = len(list(jay_corpus_path.glob("*.txt")))
    # madison_corpus_size = len(list(madison_corpus_path.glob("*.txt")))
    #
    # # RANKED RETRIEVAL
    #
    # hamilton_index_writer = DiskIndexWriter(hamilton_index_path, hamilton_document_weights,
    #                                         hamilton_document_tokens_length_per_document,
    #                                         hamilton_byte_size_d, hamilton_average_tftd,
    #                                         hamilton_document_tokens_length_average)
    #
    # jay_index_writer = DiskIndexWriter(jay_index_path, jay_document_weights, jay_document_tokens_length_per_document,
    #                                    jay_byte_size_d, jay_average_tftd, jay_document_tokens_length_average)
    #
    # madison_index_writer = DiskIndexWriter(madison_index_path, madison_document_weights,
    #                                        madison_document_tokens_length_per_document,
    #                                        madison_byte_size_d, madison_average_tftd,
    #                                        madison_document_tokens_length_average)
    #
    # # Write Disk Positional Inverted Index once
    # if not hamilton_index_writer.posting_path.is_file():
    #     hamilton_index_writer.write_index(hamilton_index)
    #
    # # Write Disk Positional Inverted Index once
    # if not jay_index_writer.posting_path.is_file():
    #     jay_index_writer.write_index(jay_index)
    #
    # # Write Disk Positional Inverted Index once
    # if not madison_index_writer.posting_path.is_file():
    #     madison_index_writer.write_index(madison_index)
    #
    # # To write the vocab for first time
    # vocab_list_path = hamilton_index_path / "vocab_list.txt"
    # vocab = hamilton_index.vocabulary()
    # with open(vocab_list_path, 'w') as f:
    #     f.writelines('\n'.join(vocab))
    #
    # # To write the vocab for first time
    # vocab_list_path = jay_index_path / "vocab_list.txt"
    # vocab = jay_index.vocabulary()
    # with open(vocab_list_path, 'w') as f:
    #     f.writelines('\n'.join(vocab))
    #
    # # To write the vocab for first time
    # vocab_list_path = madison_index_path / "vocab_list.txt"
    # vocab = madison_index.vocabulary()
    # with open(vocab_list_path, 'w') as f:
    #     f.writelines('\n'.join(vocab))
    #
    # strategyMap = {1: DefaultStrategy, 2: TraditionalStrategy, 3: OkapiBM25Strategy, 4: WackyStrategy}
    #
    # strategy = strategyMap.get(1)
    # rankedStrategy = RankedStrategy(strategy)
    #
    # # query = "new york univers"
    # # query = "Coral Reef"
    # # query = "camping in yosemite"
    # # query = "strenuous"
    # # query = "devils postpile"
    #
    # hamilton_disk_index = DiskPositionalIndex(hamilton_index_writer)
    # jay_disk_index = DiskPositionalIndex(jay_index_writer)
    # madison_disk_index = DiskPositionalIndex(madison_index_writer)
    #
    # # TODO: What is the vocabulary here? Of all the docs in the 3 classes or just the DISPUTED docs??
    # # vocabulary = disk_index.vocabulary()
    # # # vocabulary_length = len(vocabulary)
    # # vocabulary_length = cardinality.count(vocabulary)
    # # if vocabulary_length:
    # #     vocab = vocabulary[:1000]
    # #     print("First 1000(less) terms in vocabulary(sorted): ")
    # #     print(*vocab, sep="\n")
    # #     print("Total number of vocabulary terms: ", vocabulary_length)
    # # else:
    # #     print("No vocabulary found")
    #
    # # TODO: Here for the query[the whole file is the query], loop through each document/txt file in the disputed
    # #  directory and find that docs normalized vector v(d) and get the difference |µ(c) − v(d)| for all the 3
    # #  centroids( classes). Return the smallest difference as the class. Print the class for each document.
    # # TODO: is v(d) = wdt/Ld  or v(d) = accumulator(but here we do wdt*wqt)??
    #
    # # accumulator = rankedStrategy.calculate(query, disk_index, corpus_size)
    #
    # # TODO: For hamilton class find the centroid
    # # TODO: Loop through each text file in hamilton folder and query each file
    # accumulator = {}
    # N = hamilton_corpus_size
    # token_processor = NewTokenProcessor()
    # for term in set(query.split(" ")):
    #     tokenized_term = TermLiteral(term, False, mode='rank')
    #     postings = tokenized_term.get_postings(hamilton_disk_index, token_processor=token_processor)
    #     # postings = disk_index.get_postings(term)
    #     dft = len(postings)
    #     wqt = ln(1 + N / dft)
    #
    #     for posting in postings:
    #         wdt = 1 + ln(posting.tftd)
    #         if posting.doc_id not in accumulator.keys():
    #             accumulator[posting.doc_id] = 0.
    #         accumulator[posting.doc_id] += (wdt * wqt)
    #
    # for doc_id in accumulator.keys():
    #     Ld = disk_index.get_doc_info(doc_id, "Ld")
    #     accumulator[doc_id] /= Ld
    #
    # # print("Returned value: ", accumulator)
    #
    # K = 10
    # heap = [(score, doc_id) for doc_id, score in accumulator.items()]
    # print(f"Top {K} documents for query: {query}")
    # for k_documents in nlargest(K, heap):
    #     score, doc_id = k_documents
    #     print(f"Doc Title: {corpus.get_document(doc_id).title}, Score: {score}")
    #     # print(f"Doc id: {doc_id}, Score: {score}")
