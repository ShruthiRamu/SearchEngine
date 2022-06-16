from pathlib import Path
from diskindexwriter import DiskIndexWriter
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.diskpositionalindex import DiskPositionalIndex
from indexes.invertedindex import InvertedIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser, PhraseLiteral
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor
from numpy import log as ln
from math import sqrt
from typing import List
from struct import pack, unpack
from heapq import nlargest


def index_corpus(corpus: DocumentCorpus) -> (Index, List[float]):
    print("Indexing...")
    token_processor = NewTokenProcessor()
    index = PositionalInvertedIndex()
    document_weights = [] # Ld for all documents in corpus
    for d in corpus:
        term_tftd = {} # Term -> Term Frequency in a document
        stream = EnglishTokenStream(d.get_content())
        position = 1
        for token in stream:
            terms = token_processor.process_token(token)
            for term in terms:
                if term not in term_tftd.keys():
                    term_tftd[term] = 0 #Initialization
                term_tftd[term] += 1
                index.add_term(term=term, position=position, doc_id=d.id)
            position += 1

        Ld = 0
        for tftd in term_tftd.values():
            wdt = 1 + ln(tftd)
            wdt = wdt**2
            Ld += wdt
        Ld = sqrt(Ld)
        document_weights.append(Ld)

    return index, document_weights


" Main Application of Search Engine "

if __name__ == "__main__":

    # corpus_path = Path("dummytextfiles")
    # corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    corpus_path = Path("all-nps-sites-extracted")
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    index, document_weights = index_corpus(corpus)

    #db_path = Path('term_byteposition.db')
    #if db_path.is_file():
    #    db_path.unlink()

    b_tree_exist = True
    doc_weights_exist = False

    index_path = corpus_path / "index" / "postings.bin"
    index_writer = DiskIndexWriter(index_path, b_tree_exist, doc_weights_exist, document_weights)
    # Write Disk Positional Inverted Index once
    # index_writer.write_index(index, index_path)

    #query = "new york univers"
    query = "camp in yosemit"
    disk_index = DiskPositionalIndex(index_writer)

    # ******** RANKED RETRIEVAL ALGORITHM ********
    accumulator = {}
    N = index_writer.corpus_size
    print(f"No. of documents in corpus: {N}")
    for term in set(query.split(" ")):
        postings = disk_index.get_postings(term)
        dft = len(postings)
        wqt = ln(1 + N / dft)

        for posting in postings:
            wdt = 1 + ln(posting.tftd)
            if posting.doc_id not in accumulator.keys():
                accumulator[posting.doc_id] = 0.
            accumulator[posting.doc_id] += (wdt * wqt)

    for doc_id, accum in accumulator.items():
        Ld = disk_index.get_doc_weight(doc_id)
        accum /= Ld

    K = 10
    heap = [(score, doc_id) for doc_id, score in accumulator.items()]
    print(f"Top {K} documents for query: {query}")
    for k_documents in nlargest(K, heap):
        score, doc_id = k_documents
        print(f"Doc Title: {corpus.get_document(doc_id).title}, Score: {score}")



    #corpus_path = Path('dummytextfiles')
    #corpus_path = Path('dummytextfiles')
    #d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    #index, document_weights = index_corpus(d)

    # JUST REMOVE IF EXIST
    #db_path = Path('term_byteposition.db')
    #if db_path.is_file():
    #    db_path.unlink()

    #print(f"Document Weights: ", document_weights)
    #index_writer = DiskIndexWriter(document_weights)
    #index_path = Path('dummytextfiles/index/postings.bin')

    # with open("docWeights.bin", "rb") as f:
    #     print(unpack(">d", f.read(8)))
    #     print(unpack(">d", f.read(8)))
    #     print(unpack(">d", f.read(8)))
    #     print(unpack(">d", f.read(8)))
    #     print(unpack(">d", f.read(8)))

    # Write to disk
    #index_writer.write_index(index, index_path)

    # print("Term -> Byte Position Mapping: ")
    #print(index_writer.b_tree)
    #term = "new"
    #print(f"Byte Position of {term}: {index_writer.get_byte_position(term)}")
    #term = "york"
    #print(f"Byte Position of {term}: {index_writer.get_byte_position(term)}")
    # term = "california"
    # print(f"Byte Position of {term}: {index_writer.get_byte_position(term)}")

    # query = "new york university"
    # disk_index = DiskPositionalIndex(index_writer)
    # # Ranked Retrieval Algorithm
    # accumulator = {}
    # N = 5  # Corpus Size TO BE UPDATED
    # # Distinct terms in query
    # for term in set(query.split(" ")):
    #     dft = len(index[term])
    #     wqt = ln(1 + N / dft)
    #     for posting in index[term]:
    #         tftd = len(posting.positions)
    #         wdt = 1 + ln(tftd)
    #         if posting.doc_id not in accumulator.keys():
    #             accumulator[posting.doc_id] = 0.
    #         accumulator[posting.doc_id] += (wdt * wqt)
    #
    # for accum in accumulator.values():
    #     accum /= L
    #
    # K = 10
    # heap = [(score, doc_id) for doc_id, score in accumulator.items()]
    # print(f"Top {K} documents for query: {query}")
    # for k_documents in nlargest(K, heap):
    #     score, doc_id = k_documents
    #     print(f"Doc ID: {doc_id}, Score: {score}")
