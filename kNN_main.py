import os

from diskindexwriter import DiskIndexWriter
from documents.corpus import DocumentCorpus
from documents.directorycorpus import DirectoryCorpus
from feature_selection import select_features
from indexes.diskpositionalindex import DiskPositionalIndex
from indexes.index import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from text.englishtokenstream import EnglishTokenStream
from text.newtokenprocessor import NewTokenProcessor
from typing import List, Tuple
from numpy import log as ln
from math import sqrt
from pathlib import Path
from heapq import nlargest


def index_corpus(corpus: DocumentCorpus) -> Tuple[Index, List[float], List[int], int, float, float]:
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
                # TODO: Add biword index
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


if __name__ == "__main__":
    corpus_dir = Path('federalist-papers2')
    doc_list = []

    doc_count = 1
    while doc_count < 86:

        # skip disputed documents
        if 17 < doc_count < 21:
            doc_count = 21
        elif 48 < doc_count < 58:
            doc_count = 58
        elif 61 < doc_count < 64:
            doc_count = 64

        paper = "paper_" + str(doc_count)
        corpus_path = corpus_dir / paper

        corpus = DirectoryCorpus.load_text_directory(corpus_path, '.txt')
        num_docs = len(list(corpus_path.glob("*.txt")))
        index_path = corpus_path / ("index")
        index_path = index_path.resolve()

        positional_index, document_weights, document_tokens_length_per_document, byte_size_ds, average_tftds, document_tokens_length_average = index_corpus(
            corpus)

        if not index_path.is_dir():
            index_path.mkdir()
        index_writer = DiskIndexWriter(index_path, document_weights=document_weights,
                                       docLengthd=document_tokens_length_per_document,
                                       byteSized=byte_size_ds, average_tftd=average_tftds,
                                       document_tokens_length_average=document_tokens_length_average)
        if not index_writer.posting_path.is_file():
            index_writer.write_index(positional_index)

        disk_index = DiskPositionalIndex(index_writer, num_docs=num_docs)

        # Create v(d) for disputed documents
        disputed_corpus_path = Path("dummy-disputed2")
        disputed_corpus = DirectoryCorpus.load_text_directory(disputed_corpus_path, ".txt")
        num_docs = len(list(disputed_corpus_path.glob("*.txt")))
        index_path = disputed_corpus_path / "index"
        index_path = index_path.resolve()

        positional_index, document_weights, document_tokens_length_per_document, byte_size_ds, average_tftds, document_tokens_length_average = \
            index_corpus(disputed_corpus)

        if not index_path.is_dir():
            index_path.mkdir()
        index_writer = DiskIndexWriter(index_path, document_weights=document_weights,
                                       docLengthd=document_tokens_length_per_document,
                                       byteSized=byte_size_ds, average_tftd=average_tftds,
                                       document_tokens_length_average=document_tokens_length_average)
        if not index_writer.posting_path.is_file():
            index_writer.write_index(positional_index)

        disputed_disk_index = DiskPositionalIndex(index_writer, num_docs=num_docs)

        # get vocab for each disputed document
        vocabulary = disputed_disk_index.vocabulary()
        vd_disputed = {}
        # For each term in the vocabulary find the wdt
        for term in vocabulary:
            postings = disputed_disk_index.get_postings(term=term)
            for posting in postings:
                wdt = 1 + ln(posting.tftd)
                Ld = disputed_disk_index.get_doc_info(posting.doc_id, "Ld")
                # Update the components for the term
                vd_disputed[term] = wdt / Ld

        # get vocab for non disputed document
        vocabulary2 = disk_index.vocabulary()
        vd_nondisputed = {}
        # For each term in the vocabulary find the wdt
        for term in vocabulary2:
            postings = disk_index.get_postings(term=term)
            for posting in postings:
                wdt = 1 + ln(posting.tftd)
                Ld = disk_index.get_doc_info(posting.doc_id, "Ld")
                # Update the components for the term
                vd_nondisputed[term] = wdt / Ld

        distances = ()
        distance = 0
        for key, value in vd_disputed.items():
            # Get the first value for the term from nondisputed document
            if not vd_nondisputed.get(key):
                first_value = 0
            else:
                first_value = vd_nondisputed.get(key)
            # Get the second value for the term from the v(d) of disputed document
            second_value = value

            # Subtract the values
            difference = first_value - second_value

            # square the difference
            squared_difference = difference ** 2

            # add it to the final result
            distance += squared_difference
        distance = sqrt(distance)
        distances = (doc_count, distance)
        doc_list.append(distances)
        doc_count += 1

    lowest = (0,1)
    for i in doc_list:
        # if i[1] < lowest[1]:
        #    lowest = i
        print(i)

    #print(lowest)
