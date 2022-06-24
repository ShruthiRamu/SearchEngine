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


def index_corpus(corpus: DocumentCorpus) -> (Index, List[float], List[int], int, float, float):
    print("Indexing..")
    token_processor = NewTokenProcessor()
    index = PositionalInvertedIndex()
    document_weights = []  # Ld for all documents in corpus
    document_tokens_length_per_document = []  # docLengthd - Number of tokens in a document
    document_tokens_length_total = 0  # total number of tokens in all the documents in corpus
    average_tftds = []  # ave(tftd) - average tftd count for a particular document
    byte_size_ds = []  # byteSized - number of bytes in the file for document d
    vd_d = {}  # to store the components for each document for each term
    vds = []  # List of vd_d [[vd1],[vd2]]
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
        for t, tftd in term_tftd.items():
            wdt = 1 + ln(tftd)
            # Update the components of the vector with wdt
            vd_d[t] = wdt
            wdt = wdt ** 2
            Ld += wdt
        Ld = sqrt(Ld)

        # find v(d)- normalized vector for the document
        for t in vd_d.keys():
            vd_d[t] = vd_d[t] / Ld  # Neal gets this from disk index and also gets wdt from the disk postings(maybe
            # do this in the main)

        # square all the vd_d and add them to get 1 to verify
        # sum = 0
        # for t in vd_d.keys():
        #     sum += vd_d[t] ** 2
        # print("Sum: ", sum)  # The sum = 1.0001635188916558 is this okay??
        #
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

    # sorted_vds = []
    # for vd in vds:
    #     s = {k: vd[k] for k in sorted(vd)}
    #     sorted_vds.append(s)

    # Add all the v(d) values of each document for each term
    # result = dict(reduce(lambda x, y: Counter(x) + Counter(y), sorted_vds))

    # Add all the v(d) values for each term
    centroid = {}
    for elm in vds:
        for k, v in elm.items():

            # Initialise it if it doesn't exist
            if k not in centroid:
                centroid[k] = 0

            # accumulate sum separately
            centroid[k] += v

    # Dc is the length of the corpus of the class/folder
    Dc = len(corpus)

    # Divide by the Dc - the total number of documents in the corpus
    for i in centroid:
        centroid[i] = centroid[i] / Dc

    print(f"Corpus: {corpus}, centroid: {centroid}")

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

    hamilton_corpus_path = Path("federalist-papers/HAMILTON")
    hamilton_corpus = DirectoryCorpus.load_text_directory(hamilton_corpus_path, ".txt")
    hamilton_index, hamilton_document_weights, hamilton_document_tokens_length_per_document, hamilton_byte_size_d, hamilton_average_tftd, \
    hamilton_document_tokens_length_average = index_corpus(hamilton_corpus)

    jay_corpus_path = Path("federalist-papers/JAY")
    jay_corpus = DirectoryCorpus.load_text_directory(jay_corpus_path, ".txt")
    jay_index, jay_document_weights, jay_document_tokens_length_per_document, jay_byte_size_d, jay_average_tftd, \
    jay_document_tokens_length_average = index_corpus(jay_corpus)

    madison_corpus_path = Path("federalist-papers/MADISON")
    madison_corpus = DirectoryCorpus.load_text_directory(madison_corpus_path, ".txt")
    madison_index, madison_document_weights, madison_document_tokens_length_per_document, madison_byte_size_d, madison_average_tftd, \
    madison_document_tokens_length_average = index_corpus(madison_corpus)

    # Calculate wdt for all the documents in the DISPUTED Directory
    disputed_corpus_path = Path("federalist-papers/DISPUTED")
    disputed_corpus = DirectoryCorpus.load_text_directory(disputed_corpus_path, ".txt")
    disputed_index, disputed_document_weights, disputed_document_tokens_length_per_document, disputed_byte_size_d, disputed_average_tftd, \
    disputed_document_tokens_length_average = index_corpus(disputed_corpus)

    # TODO: Go through each document in the DISPUTED folder find the vector v(d) and finally find the euclidian length.
    #  For each term in the document subtract the the centroid value and the disputed v(d) value
    #  and add all them and find the square root for part B?? d ^ 2 = (centroid(t1)-vd(t1))^2+(centroid(t2)-vd(t2))^2...
    #  Do this for each class

    hamilton_index_path = hamilton_corpus_path / "index"
    hamilton_index_path = hamilton_index_path.resolve()
    if not hamilton_index_path.is_dir():
        hamilton_index_path.mkdir()

    jay_index_path = jay_corpus_path / "index"
    jay_index_path = jay_index_path.resolve()
    if not jay_index_path.is_dir():
        jay_index_path.mkdir()

    madison_index_path = madison_corpus_path / "index"
    madison_index_path = madison_index_path.resolve()
    if not madison_index_path.is_dir():
        madison_index_path.mkdir()

    hamilton_corpus_size = len(list(hamilton_corpus_path.glob("*.txt")))
    jay_corpus_size = len(list(jay_corpus_path.glob("*.txt")))
    madison_corpus_size = len(list(madison_corpus_path.glob("*.txt")))

    # RANKED RETRIEVAL

    hamilton_index_writer = DiskIndexWriter(hamilton_index_path, hamilton_document_weights,
                                            hamilton_document_tokens_length_per_document,
                                            hamilton_byte_size_d, hamilton_average_tftd,
                                            hamilton_document_tokens_length_average)

    jay_index_writer = DiskIndexWriter(jay_index_path, jay_document_weights, jay_document_tokens_length_per_document,
                                       jay_byte_size_d, jay_average_tftd, jay_document_tokens_length_average)

    madison_index_writer = DiskIndexWriter(madison_index_path, madison_document_weights,
                                           madison_document_tokens_length_per_document,
                                           madison_byte_size_d, madison_average_tftd,
                                           madison_document_tokens_length_average)

    # Write Disk Positional Inverted Index once
    if not hamilton_index_writer.posting_path.is_file():
        hamilton_index_writer.write_index(hamilton_index)

    # Write Disk Positional Inverted Index once
    if not jay_index_writer.posting_path.is_file():
        jay_index_writer.write_index(jay_index)

    # Write Disk Positional Inverted Index once
    if not madison_index_writer.posting_path.is_file():
        madison_index_writer.write_index(madison_index)

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
    strategyMap = {1: DefaultStrategy, 2: TraditionalStrategy, 3: OkapiBM25Strategy, 4: WackyStrategy}

    # Always default here
    strategy = strategyMap.get(1)
    rankedStrategy = RankedStrategy(strategy)

    # TODO: Not sure what the query here would be or do we even need to do ranked retrieval here???
    query = "devils postpile"

    hamilton_disk_index = DiskPositionalIndex(hamilton_index_writer)
    jay_disk_index = DiskPositionalIndex(jay_index_writer)
    madison_disk_index = DiskPositionalIndex(madison_index_writer)

    # vocabulary = disk_index.vocabulary()
    # # vocabulary_length = len(vocabulary)
    # vocabulary_length = cardinality.count(vocabulary)
    # if vocabulary_length:
    #     vocab = vocabulary[:1000]
    #     print("First 1000(less) terms in vocabulary(sorted): ")
    #     print(*vocab, sep="\n")
    #     print("Total number of vocabulary terms: ", vocabulary_length)
    # else:
    #     print("No vocabulary found")

    # TODO: Here loop through each document/txt file in the disputed
    #  directory and find that docs normalized vector v(d) and get the difference |µ(c) − v(d)| for all the 3
    #  centroids(classes). Find the euclidian length for part B

    # TODO: For hamilton class find the centroid [Can I do it while creating the index in the index_corpus??]
    # Say JAY has 3 documents d1, d2, d3
    # Say all of the JAY's documents have 5 terms
    # V(d1) = wdt1/Ld1, wdt2/Ld1, wdt3/Ld1, wdt4/Ld1, wdt5/Ld1
    # V(d2) = wdt1/Ld2, wdt2/Ld2, wdt3/Ld2, wdt4/Ld2, wdt5/Ld2
    # V(d3) = wdt1/Ld3, wdt2/Ld3, wdt3/Ld3, wdt4/Ld3, wdt5/Ld3

    # Here Dc = 3
    # For JAY: Centroid = (wdt1/Ld1 + wdt1/Ld2 + wdt1/Ld3)/Dc, (wdt2/Ld1 + wdt2/Ld2 + wdt2/Ld3)/Dc,
    # (wdt3/Ld1 + wdt3/Ld2 + wdt3/Ld3)/Dc, (wdt4/Ld1 + wdt4/Ld2 + wdt4/Ld3)/Dc, (wdt5/Ld1 + wdt5/Ld2 + wdt5/Ld3)/Dc

    # TODO: Go through each document in the DISPUTED folder find the vector v(d) for it
    #  and finally find the euclidian length.
    #  For each term in the document subtract the the centroid value and the disputed v(d) or wdt value???
    #  and add all them and find the square root for part B?? d ^ 2 = (centroid(t1)-vd(t1))^2+(centroid(t2)-vd(t2))^2...
    #  Do this all 3 classes to get 3 values and smallest is the class that document belongs to.

    # Default ranked retrieval strategy
    accumulator = {}
    N = hamilton_corpus_size
    token_processor = NewTokenProcessor()
    for term in set(query.split(" ")):
        tokenized_term = TermLiteral(term, False, mode='rank')
        postings = tokenized_term.get_postings(hamilton_disk_index, token_processor=token_processor)
        # postings = disk_index.get_postings(term)
        dft = len(postings)
        wqt = ln(1 + N / dft)

        for posting in postings:
            wdt = 1 + ln(posting.tftd)
            if posting.doc_id not in accumulator.keys():
                accumulator[posting.doc_id] = 0.
            accumulator[posting.doc_id] += (wdt * wqt)

    for doc_id in accumulator.keys():
        Ld = hamilton_disk_index.get_doc_info(doc_id, "Ld")
        accumulator[doc_id] /= Ld

    # print("Returned value: ", accumulator)

    K = 10
    heap = [(score, doc_id) for doc_id, score in accumulator.items()]
    print(f"Top {K} documents for query: {query}")
    for k_documents in nlargest(K, heap):
        score, doc_id = k_documents
        print(f"Doc Title: {hamilton_corpus.get_document(doc_id).title}, Score: {score}")
        # print(f"Doc id: {doc_id}, Score: {score}")
