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

    corpus_path = Path("relevance_cranfield")
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    index, document_weights, document_tokens_length_per_document, byte_size_d, average_tftd, \
    document_tokens_length_average = index_corpus(corpus)

    index_path = corpus_path / "index"
    index_path = index_path.resolve()
    if not index_path.is_dir():
        index_path.mkdir()

    # corpus_size = len(document_weights)
    corpus_size = len(list(corpus_path.glob("*.json")))

    # RANKED RETRIEVAL

    index_writer = DiskIndexWriter(index_path, document_weights, document_tokens_length_per_document,
                                   byte_size_d, average_tftd, document_tokens_length_average)

    # Write Disk Positional Inverted Index once
    if not index_writer.posting_path.is_file():
        index_writer.write_index(index)

    disk_index = DiskPositionalIndex(index_writer, num_docs=corpus_size)

    strategyMap = {1: DefaultStrategy, 2: TraditionalStrategy, 3: OkapiBM25Strategy, 4: WackyStrategy}

    # Open the queries file and each line is a query. Loop through each line as a single query and calculate
    #  MAP for each query
    f = open("relevance_cranfield/relevance/queries", "r")
    queries = f.readlines()
    f.close()

    # Go through the relevant documents from the qrel file, each line corresponds to single query

    f = open("relevance_cranfield/relevance/qrel", "r")
    relevant_documents = f.readlines()
    f.close()

    # count = 0
    # # Strips the newline character
    # for line in relevant_documents:
    #     count += 1
    #     print("Line{}: {}".format(count, line.strip()))

    # For default strategy
    strategy = strategyMap.get(1)
    rankedStrategy_default = RankedStrategy(strategy)

    # For traditional strategy
    strategy = strategyMap.get(2)
    rankedStrategy_traditional = RankedStrategy(strategy)

    # For okapi strategy
    strategy = strategyMap.get(3)
    rankedStrategy_okapi = RankedStrategy(strategy)

    # For wacky strategy
    strategy = strategyMap.get(4)
    rankedStrategy_wacky = RankedStrategy(strategy)

    total_average_precision = 0

    response_time = 0
    mean_response_time = 0
    print("\n############### Default STRATEGY ####################\n")

    # loop through each query
    for i in range(0, len(queries)):

        # get the query i
        query = queries[i]

        # Relevant documents for the query i
        relevant_document = relevant_documents[i].split()
        for j in range(0, len(relevant_document)):
            relevant_document[j] = int(relevant_document[j])

        ########################## Default ##############################

        start = time_ns()
        # For default strategy
        accumulator = rankedStrategy_default.calculate(query, disk_index, corpus_size)
        end = time_ns()
        #print(f"Ranked Retrieval took: {(end - start) / 1e+9} secs\n")
        response_time += (end - start) / 1e+9

        query_result_documents = []

        K = 50
        heap = [(score, doc_id) for doc_id, score in accumulator.items()]
        #print(f"Top {K} documents for query: {query}")
        for k_documents in nlargest(K, heap):
            score, doc_id = k_documents
            # print(f"Doc filename: {corpus.get_document(doc_id).get_file_name()}, Score: {score}")
            query_result_documents.append(corpus.get_document(doc_id).get_file_name())

        for j in range(0, len(query_result_documents)):
            query_result_documents[j] = int(query_result_documents[j])

        # Calculate the average precision for the query
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

        # print(f"Query: {query}Average precision: {average_precision} \n")

    print("Total average precision: ", total_average_precision)
    print("Total number of queries: ", len(queries))
    MAP = total_average_precision / len(queries)
    print(f"MAP: {MAP}")

    mean_response_time = response_time / len(queries)
    average_throughput = 1 / mean_response_time

    print(f"Mean Response Time to satisfy a query:{mean_response_time}")
    print(f"Throughput(queries/second) of the system:{average_throughput} ")

    # ############################## OKAPI Strategy ##############################################
    print("\n############### OKAPI STRATEGY ####################\n")

    total_average_precision = 0
    response_time = 0
    mean_response_time = 0
    # loop through each query
    for i in range(0, len(queries)):

        # get the query i
        query = queries[i]

        # Relevant documents for the query i
        relevant_document = relevant_documents[i].split()
        for j in range(0, len(relevant_document)):
            relevant_document[j] = int(relevant_document[j])

        start = time_ns()
        # For default strategy
        accumulator = rankedStrategy_okapi.calculate(query, disk_index, corpus_size)
        end = time_ns()
        #print(f"Ranked Retrieval took: {(end - start) / 1e+9} secs\n")
        response_time += (end - start) / 1e+9

        query_result_documents = []

        K = 50
        heap = [(score, doc_id) for doc_id, score in accumulator.items()]
        #print(f"Top {K} documents for query: {query}")
        for k_documents in nlargest(K, heap):
            score, doc_id = k_documents
            # print(f"Doc filename: {corpus.get_document(doc_id).get_file_name()}, Score: {score}")
            query_result_documents.append(corpus.get_document(doc_id).get_file_name())

        for j in range(0, len(query_result_documents)):
            query_result_documents[j] = int(query_result_documents[j])

        # Calculate the average precision for the query
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

        # print(f"Query: {query}Average precision: {average_precision} \n")

    print("Total average precision: ", total_average_precision)
    print("Total number of queries: ", len(queries))
    MAP = total_average_precision / len(queries)
    print(f"MAP: {MAP}")

    mean_response_time = response_time / len(queries)
    average_throughput = 1 / mean_response_time

    print(f"Mean Response Time to satisfy a query:{mean_response_time}")
    print(f"Throughput(queries/second) of the system:{average_throughput} ")

    # ####################### Traditional-tf-idf ###################################

    print("\n############### TRADITIONAL STRATEGY ####################\n")
    total_average_precision = 0
    response_time = 0
    mean_response_time = 0
    # loop through each query
    for i in range(0, len(queries)):

        # get the query i
        query = queries[i]

        # Relevant documents for the query i
        relevant_document = relevant_documents[i].split()
        for j in range(0, len(relevant_document)):
            relevant_document[j] = int(relevant_document[j])

        start = time_ns()
        # For default strategy
        accumulator = rankedStrategy_traditional.calculate(query, disk_index, corpus_size)
        end = time_ns()
        #print(f"Ranked Retrieval took: {(end - start) / 1e+9} secs\n")
        response_time += (end - start) / 1e+9

        query_result_documents = []

        K = 50
        heap = [(score, doc_id) for doc_id, score in accumulator.items()]
        #print(f"Top {K} documents for query: {query}")
        for k_documents in nlargest(K, heap):
            score, doc_id = k_documents
            # print(f"Doc filename: {corpus.get_document(doc_id).get_file_name()}, Score: {score}")
            query_result_documents.append(corpus.get_document(doc_id).get_file_name())

        for j in range(0, len(query_result_documents)):
            query_result_documents[j] = int(query_result_documents[j])

        # Calculate the average precision for the query
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

        # print(f"Query: {query}Average precision: {average_precision} \n")

    print("Total average precision: ", total_average_precision)
    print("Total number of queries: ", len(queries))
    MAP = total_average_precision / len(queries)
    print(f"MAP: {MAP}")

    mean_response_time = response_time / len(queries)
    average_throughput = 1 / mean_response_time

    print(f"Mean Response Time to satisfy a query:{mean_response_time}")
    print(f"Throughput(queries/second) of the system:{average_throughput} ")

    # ####################### Wacky ###################################

    print("\n############### WACKY STRATEGY ####################\n")
    total_average_precision = 0
    response_time = 0
    mean_response_time = 0
    # loop through each query
    for i in range(0, len(queries)):

        # get the query i
        query = queries[i]

        # Relevant documents for the query i
        relevant_document = relevant_documents[i].split()
        for j in range(0, len(relevant_document)):
            relevant_document[j] = int(relevant_document[j])

        start = time_ns()
        # For default strategy
        accumulator = rankedStrategy_wacky.calculate(query, disk_index, corpus_size)
        end = time_ns()
        #print(f"Ranked Retrieval took: {(end - start) / 1e+9} secs\n")
        response_time += (end - start) / 1e+9


        query_result_documents = []

        K = 50
        heap = [(score, doc_id) for doc_id, score in accumulator.items()]
        #print(f"Top {K} documents for query: {query}")
        for k_documents in nlargest(K, heap):
            score, doc_id = k_documents
            # print(f"Doc filename: {corpus.get_document(doc_id).get_file_name()}, Score: {score}")
            query_result_documents.append(corpus.get_document(doc_id).get_file_name())

        for j in range(0, len(query_result_documents)):
            query_result_documents[j] = int(query_result_documents[j])

        # Calculate the average precision for the query
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

        # print(f"Query: {query}Average precision: {average_precision} \n")

    print("Total average precision: ", total_average_precision)
    print("Total number of queries: ", len(queries))
    MAP = total_average_precision / len(queries)
    print(f"MAP: {MAP}")

    mean_response_time = response_time / len(queries)
    average_throughput = 1 / mean_response_time

    print(f"Mean Response Time to satisfy a query:{mean_response_time}")
    print(f"Throughput(queries/second) of the system:{average_throughput} ")


