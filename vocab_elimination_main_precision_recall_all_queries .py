from pathlib import Path
from diskindexwriter import DiskIndexWriter
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.diskpositionalindex import DiskPositionalIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import TermLiteral
from ranked_strategy import DefaultStrategy, RankedStrategy, TraditionalStrategy, OkapiBM25Strategy, WackyStrategy
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor
from numpy import log as ln, arange, insert, concatenate
from math import sqrt
from typing import List
from heapq import nlargest
from statistics import mean, median, mode
from pandas import DataFrame


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

    corpus_size = len(list(corpus_path.glob("*.json")))

    index_writer = DiskIndexWriter(index_path, document_weights, document_tokens_length_per_document,
                                   byte_size_d, average_tftd, document_tokens_length_average)

    # Write Disk Positional Inverted Index once
    if not index_writer.posting_path.is_file():
        index_writer.write_index(index)

    disk_index = DiskPositionalIndex(index_writer, num_docs=corpus_size)

    # TODO: Open the queries file and each line is a query. Loop through each line as a single query and calculate
    #  MAP for each query
    f = open("relevance_cranfield/relevance/queries", "r")
    queries = f.readlines()
    f.close()

    # TODO: Go through the relevant documents from the qrel file, each line corresponds to single query
    f = open("relevance_cranfield/relevance/qrel", "r")
    relevant_documents = f.readlines()
    f.close()

    # N = corpus_size
    # print("Corpus Size: ", N)
    # vocab = index.vocabulary()
    # dfts = []
    # wqts = []
    # for term in vocab:
    #     postings = index.get_positional_postings(term)
    #     dft = len(postings)
    #     if dft != 0:
    #         dfts.append(dft)
    #         wqt = ln(1 + N / dft)
    #         wqts.append(wqt)
    #
    # print("Avg doc freq. ", mean(dfts))
    # print("Median doc freq. ", median(dfts))
    # print("Mode doc freq. ", mode(dfts))
    # #print("Document Frequencies: ", dfts)
    # print("Mean Wqts. ", mean(wqts))
    # print("Median Wqts. ", median(wqts))
    # print("Mode Wqts. ", mode(wqts))

    #experimental_thresholds = arange(0.1, 1.5, 0.1)
    # First one is EXACT RANKED RETRIEVAL
    #experimental_thresholds = insert(experimental_thresholds, 0, -9999.999)
    #experimental_thresholds = concatenate((experimental_thresholds, experimental_thresholds))
    # print("Wqts: ", wqts)
    #half_length = int(len(experimental_thresholds) / 2)

    strategies = ['DEFAULT', 'OKAPI']

    MAPs = []
    MRTs = []
    throughputs = []

    queries = queries[:1] # Only first queries
    num_itr = 30

    for idx, strategy in enumerate(strategies):
        print()
        print("*"*20 + f" STRATEGY: {strategy} " + "*"*20)
        RESPONSE_TIMES = []
        for iii in range(num_itr):
            # RANKED RETRIEVAL
            #print(f"\n{retrieval_mode} RANK RETRIEVAL")
            total_average_precision = 0
            response_time = 0
            num_queries = len(queries)
            # loop through each query
            for i in range(0, num_queries):
                # get the query i
                query = queries[i]

                # Relevant documents for the query i
                relevant_document = relevant_documents[i].split()
                for j in range(0, len(relevant_document)):
                    relevant_document[j] = int(relevant_document[j])

                start = time_ns()

                if strategy == "DEFAULT":
                    # DEFAULT:
                    #print("Default Strategy")
                    accumulator = {}
                    N = corpus_size
                    token_processor = NewTokenProcessor()
                    for term in set(query.split(" ")):
                        tokenized_term = TermLiteral(term, False, mode='rank')
                        postings = tokenized_term.get_postings(disk_index, token_processor=token_processor)
                        # postings = disk_index.get_postings(term)
                        dft = len(postings)
                        if dft != 0:
                            wqt = ln(1 + N / dft)
                        else:
                            wqt = 0

                        if wqt < 1.1:
                            continue

                        for posting in postings:
                            wdt = 1 + ln(posting.tftd)
                            if posting.doc_id not in accumulator.keys():
                                accumulator[posting.doc_id] = 0.
                            accumulator[posting.doc_id] += (wdt * wqt)

                    for doc_id in accumulator.keys():
                        Ld = disk_index.get_doc_info(doc_id, "Ld")
                        accumulator[doc_id] /= Ld

                else:
                    # OKAPI
                    #print("OKAPI")
                    accumulator = {}
                    N = corpus_size
                    token_processor = NewTokenProcessor()

                    for term in set(query.split(" ")):
                        tokenized_term = TermLiteral(term, False, mode='rank')
                        postings = tokenized_term.get_postings(disk_index, token_processor=token_processor)
                        dft = len(postings)
                        if dft != 0:
                            wqt = max(0.1, ln((N - dft + 0.5) / (dft + 0.5)))
                        else:
                            wqt = 0

                        if wqt < 0.4:
                            continue

                        for posting in postings:
                            docLength = disk_index.get_doc_info(posting.doc_id, "docLength")
                            doc_tokens_len_avg = disk_index.get_avg_tokens_corpus()
                            denominator = (1.2 * (0.25 + (0.75 * (docLength / doc_tokens_len_avg)))) + posting.tftd
                            wdt = (2.2 * posting.tftd) / denominator
                            if posting.doc_id not in accumulator.keys():
                                accumulator[posting.doc_id] = 0.
                            accumulator[posting.doc_id] += (wdt * wqt)

                    for doc_id in accumulator.keys():
                        Ld = 1
                        accumulator[doc_id] /= Ld

                end = time_ns()
                # print(f"Ranked Retrieval took: {(end - start) / 1e+9} secs\n")
                response_time += (end - start) / 1e+9
                RESPONSE_TIMES.append(response_time)
                query_result_documents = []
                K = 50
                heap = [(score, doc_id) for doc_id, score in accumulator.items()]
                result_docs = []
                for k_documents in nlargest(K, heap):
                    score, doc_id = k_documents
                    doc = corpus.get_document(doc_id)
                    result_docs.append(doc.get_title())
                    #print(f"Doc filename: {corpus.get_document(doc_id).get_file_name()}, Score: {score}")
                    query_result_documents.append(doc.get_file_name())

                for j in range(0, len(query_result_documents)):
                    query_result_documents[j] = int(query_result_documents[j])

                # TODO: Calculate the average precision for the first query
                total_relevant_documents = len(relevant_document)

                # Calculate the precision
                precisions = []
                relevant_count = 0
                sum = 0
                if strategy == "DEFAULT" and iii == 0:
                    print(f"Search results ({len(query_result_documents)} documents): ")
                for j in range(0, len(query_result_documents)):
                    relevance_marker = "x"
                    if query_result_documents[j] in relevant_document:
                        relevance_marker = u'\u2713'
                        relevant_count += 1
                        precision = relevant_count / (j + 1)
                        sum += precision
                        precisions.append(precision)
                    else:
                        precisions.append(relevant_count / (j + 1))

                    if strategy == "DEFAULT" and iii == 0:
                        print(f"[{j+1}] {result_docs[j]} ({relevance_marker})")

                # Divide by the total number of relevant documents for average precision for the query
                average_precision = sum / total_relevant_documents
                if iii == 0:
                    print(f"\nAverage Precision: {average_precision}")
                total_average_precision += average_precision

        #print(f"Length of response times: {len(RESPONSE_TIMES)}")
        print(f"Throughput: {1 / mean(RESPONSE_TIMES)}")

            # print(f"Query: {query}Average precision: {average_precision} \n")

        # print("Total average precision: ", total_average_precision)
        # print("Total number of queries: ", len(queries))


        #print(f"\nThreshold: {threshold}")
    MAP = total_average_precision / num_queries
    MAPs.append(MAP)
    #print(f"MAP: {MAP}")
    mean_response_time = response_time / num_queries
    MRTs.append(mean_response_time)
    #print(f"Mean Response time to satisfy a query: {mean_response_time}")
    throughput = 1 / mean_response_time
    throughputs.append(throughput)
    #print(f"Throughput of the system: {throughput}")


    # df = DataFrame(data={
    #     'Threshold': experimental_thresholds,
    #     'Mean Average Precision': MAPs,
    #     'Mean Response Time': MRTs,
    #     'Throughput': throughputs
    # })
    # df.to_csv("vocab_elimination_experiments.csv", index=False)
