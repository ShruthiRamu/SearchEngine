from pathlib import Path
from diskindexwriter import DiskIndexWriter
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.diskpositionalindex import DiskPositionalIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from ranked_strategy import DefaultStrategy, RankedStrategy, TraditionalStrategy, OkapiBM25Strategy, WackyStrategy
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor
from numpy import log as ln
from math import sqrt
from typing import List
from heapq import nlargest
import matplotlib.pyplot as plt


def index_corpus(corpus: DocumentCorpus) -> (Index, List[float], List[int], int, float, float):
    print("Indexing..")
    token_processor = NewTokenProcessor()
    index = PositionalInvertedIndex()
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
    return index, document_weights, document_tokens_length_per_document, byte_size_ds, average_tftds, document_tokens_length_average


" Main Application of Search Engine "

if __name__ == "__main__":
    # Build Cranfield Corpus
    cranfield_corpus_path = Path("relevance_cranfield")
    cranfield_corpus = DirectoryCorpus.load_json_directory(cranfield_corpus_path, ".json")

    cranfield_index, document_weights, document_tokens_length_per_document, byte_size_d, average_tftd, \
    document_tokens_length_average = index_corpus(cranfield_corpus)

    index_path = cranfield_corpus_path / "index"
    index_path = index_path.resolve()
    if not index_path.is_dir():
        index_path.mkdir()

    # corpus_size = len(document_weights)
    cranfield_corpus_size = len(list(cranfield_corpus_path.glob("*.json")))

    index_writer = DiskIndexWriter(index_path, document_weights, document_tokens_length_per_document,
                                   byte_size_d, average_tftd, document_tokens_length_average)

    # Write Disk Positional Inverted Index once
    if not index_writer.posting_path.is_file():
        index_writer.write_index(cranfield_index)

    cranfield_disk_index = DiskPositionalIndex(index_writer, num_docs=cranfield_corpus_size)

    # Build Parks Corpus
    parks_corpus_path = Path("relevance_parks")
    parks_corpus = DirectoryCorpus.load_json_directory(parks_corpus_path, ".json")

    parks_index, document_weights, document_tokens_length_per_document, byte_size_d, average_tftd, \
    document_tokens_length_average = index_corpus(parks_corpus)

    index_path = parks_corpus_path / "index"
    index_path = index_path.resolve()
    if not index_path.is_dir():
        index_path.mkdir()

    # corpus_size = len(document_weights)
    parks_corpus_size = len(list(parks_corpus_path.glob("*.json")))

    index_writer = DiskIndexWriter(index_path, document_weights, document_tokens_length_per_document,
                                   byte_size_d, average_tftd, document_tokens_length_average)

    # Write Disk Positional Inverted Index once
    if not index_writer.posting_path.is_file():
        index_writer.write_index(parks_index)

    parks_disk_index = DiskPositionalIndex(index_writer, num_docs=parks_corpus_size)

    print("\n1. Cranfield Corpus")
    print("2. Parks Corpus")
    choice = int(input(">> "))

    if choice == 1:
        disk_index = cranfield_disk_index
        corpus = cranfield_corpus
        corpus_size = cranfield_corpus_size

        f = open("relevance_cranfield/relevance/queries", "r")
        queries = f.readlines()
        f.close()

        # TODO: Go through the relevant documents from the qrel file, each line corresponds to single query

        f = open("relevance_cranfield/relevance/qrel", "r")
        relevant_documents = f.readlines()
        f.close()
    elif choice == 2:
        disk_index = parks_disk_index
        corpus = parks_corpus
        corpus_size = parks_corpus_size

        f = open("relevance_parks/relevance/queries", "r")
        queries = f.readlines()
        f.close()

        # TODO: Go through the relevant documents from the qrel file, each line corresponds to single query

        f = open("relevance_parks/relevance/qrel", "r")
        relevant_documents = f.readlines()
        f.close()

    # count = 0
    # # Strips the newline character
    # for line in relevant_documents:
    #     count += 1
    #     print("Line{}: {}".format(count, line.strip()))

    strategyMap = {1: DefaultStrategy, 2: TraditionalStrategy, 3: OkapiBM25Strategy, 4: WackyStrategy}

    while True:
        print("\n1. Search a query(ranked retrieval)")
        print("2. MAP")
        print("3. Exit")
        option = int(input(">> "))

        if option == 3:
            print("Exiting the program....")
            exit(0)

        elif option == 1:

            print("\nChoose a ranking strategy:")
            print("1. Default")
            print("2. Traditional(tf-idf)")
            print("3. Okapi BM25")
            print("4. Wacky")
            choice = input(">> ")
            strategy = strategyMap.get(int(choice))

            rankedStrategy = RankedStrategy(strategy)

            print("\nEnter query: ")
            query = input(">> ")

            print(f"Query going in: {query}")
            accumulator = rankedStrategy.calculate(query, disk_index, corpus_size)

            # SHOW THE RESULTS
            K = 50
            heap = [(score, doc_id) for doc_id, score in accumulator.items()]
            print("*" * 80)
            print(f"Top {K} documents for query: {query}")
            for k_documents in nlargest(K, heap):
                score, doc_id = k_documents
                print(f"Doc Title: {corpus.get_document(doc_id).title}, Score: {score}")

        elif option == 2:
            print("\nChoose a ranking strategy:")
            print("1. Default")
            print("2. Traditional(tf-idf)")
            print("3. Okapi BM25")
            print("4. Wacky")
            choice = input(">> ")
            strategy = strategyMap.get(int(choice))

            rankedStrategy = RankedStrategy(strategy)

            total_average_precision = 0

            # loop through each query
            for i in range(0, len(queries)):

                # get the query i
                query = queries[i]

                # Relevant documents for the query i
                relevant_document = relevant_documents[i].split()
                for j in range(0, len(relevant_document)):
                    relevant_document[j] = int(relevant_document[j])

                accumulator = rankedStrategy.calculate(query, disk_index, corpus_size)

                query_result_documents = []

                K = 50
                heap = [(score, doc_id) for doc_id, score in accumulator.items()]
                # print(f"Top {K} documents for query: {query}")
                for k_documents in nlargest(K, heap):
                    score, doc_id = k_documents
                    # print(f"Doc filename: {corpus.get_document(doc_id).get_file_name()}, Score: {score}")
                    query_result_documents.append(corpus.get_document(doc_id).get_file_name())

                for j in range(0, len(query_result_documents)):
                    query_result_documents[j] = int(query_result_documents[j])

                total_relevant_documents = len(relevant_document)

                # print("\nRelevant documents found in the ranked retrieval query result: ")
                # for document in query_result_documents:
                #     if document in relevant_document:
                #         print("Doc filename: ", document)

                # Calculate the precision
                precisions = []

                relevant_count = 0
                sum = 0
                for j in range(0, len(query_result_documents)):
                    if query_result_documents[j] in relevant_document:
                        relevant_count += 1
                        precision = relevant_count / (j + 1)
                        # sum += relevant_count / (i + 1)
                        sum += precision
                        precisions.append(precision)
                    else:
                        precisions.append(relevant_count / (j + 1))
                # print("Precisions: ", precisions)
                # print("Sum: ", sum)

                # Divide by the total number of relevant documents for average precision for the query
                average_precision_default = sum / total_relevant_documents

                total_average_precision += average_precision_default

                # print(f"Query: {query}Average precision: {average_precision_default} \n")

            # print("Total average precision: ", total_average_precision)
            # print("Total number of queries: ", len(queries))
            MAP = total_average_precision / len(queries)
            print(f"MAP: {MAP}")

            # print("Calculating MAP for all the 4 formulas....")
            # For each formula calculate MAP
            # for strategy in strategyMap.values():
            #
            #     rankedStrategy = RankedStrategy(strategy)
            #     if strategy == DefaultStrategy:
            #         name = "Default"
            #     elif strategy == TraditionalStrategy:
            #         name = "Traditional"
            #     elif strategy == OkapiBM25Strategy:
            #         name = "OKAPI BM25"
            #     elif strategy == WackyStrategy:
            #         name = "Wacky"
            #
            #     total_average_precision = 0
            #
            #     # loop through each query
            #     for i in range(0, len(queries)):
            #
            #         # get the query i
            #         query = queries[i]
            #
            #         # Relevant documents for the query i
            #         relevant_document = relevant_documents[i].split()
            #         for j in range(0, len(relevant_document)):
            #             relevant_document[j] = int(relevant_document[j])
            #
            #         accumulator = rankedStrategy.calculate(query, disk_index, corpus_size)
            #
            #         query_result_documents = []
            #
            #         K = 50
            #         heap = [(score, doc_id) for doc_id, score in accumulator.items()]
            #         # print(f"Top {K} documents for query: {query}")
            #         for k_documents in nlargest(K, heap):
            #             score, doc_id = k_documents
            #             # print(f"Doc filename: {corpus.get_document(doc_id).get_file_name()}, Score: {score}")
            #             query_result_documents.append(corpus.get_document(doc_id).get_file_name())
            #
            #         for j in range(0, len(query_result_documents)):
            #             query_result_documents[j] = int(query_result_documents[j])
            #
            #         total_relevant_documents = len(relevant_document)
            #
            #         # print("\nRelevant documents found in the ranked retrieval query result: ")
            #         # for document in query_result_documents:
            #         #     if document in relevant_document:
            #         #         print("Doc filename: ", document)
            #
            #         # Calculate the precision
            #         precisions = []
            #
            #         relevant_count = 0
            #         sum = 0
            #         for j in range(0, len(query_result_documents)):
            #             if query_result_documents[j] in relevant_document:
            #                 relevant_count += 1
            #                 precision = relevant_count / (j + 1)
            #                 # sum += relevant_count / (i + 1)
            #                 sum += precision
            #                 precisions.append(precision)
            #             else:
            #                 precisions.append(relevant_count / (j + 1))
            #         # print("Precisions: ", precisions)
            #         # print("Sum: ", sum)
            #
            #         # Divide by the total number of relevant documents for average precision for the query
            #         average_precision_default = sum / total_relevant_documents
            #
            #         total_average_precision += average_precision_default
            #
            #         # print(f"Query: {query}Average precision: {average_precision_default} \n")
            #
            #     # print("Total average precision: ", total_average_precision)
            #     # print("Total number of queries: ", len(queries))
            #     MAP = total_average_precision / len(queries)
            #     print(f"Formula: {name}, MAP: {MAP}")
