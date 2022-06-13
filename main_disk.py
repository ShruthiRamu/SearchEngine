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
from struct import pack
from heapq import nlargest


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = NewTokenProcessor()
    # token_processor = BasicTokenProcessor()
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
    with open("docWeights.bin", 'wb') as f:
        for doc_weight in document_weights:
            f.write(pack('>d', float(doc_weight)))

    return index


" Main Application of Search Engine "

if __name__ == "__main__":

    #corpus_path = Path('dummytextfiles')
    corpus_path = Path('dummytextfiles')
    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(d)

    index_writer = DiskIndexWriter()
    index_path = Path('dummytextfiles/index/postings.bin')
    #print("Index path: ", index_path)
    # Write to disk
    index_writer.write_index(index, index_path)
    #print("Term -> Byte Position Mapping: ")
    #print(index_writer.b_tree)

    query = "new york university"
    disk_index = DiskPositionalIndex(index_writer)
    # Ranked Retrieval Algorithm
    accumulator = {}
    N = 5  # Corpus Size TO BE UPDATED
    # Distinct terms in query
    for term in set(query.split(" ")):
        dft = len(index[term])
        wqt = ln(1 + N / dft)
        for posting in index[term]:
            tftd = len(posting.positions)
            wdt = 1 + ln(tftd)
            if posting.doc_id not in accumulator.keys():
                accumulator[posting.doc_id] = 0.
            accumulator[posting.doc_id] += (wdt * wqt)

    for accum in accumulator.values():
        accum /= L

    K = 10
    heap = [(score, doc_id) for doc_id, score in accumulator.items()]
    print(f"Top {K} documents for query: {query}")
    for k_documents in nlargest(K, heap):
        score, doc_id = k_documents
        print(f"Doc ID: {doc_id}, Score: {score}")
