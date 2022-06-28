import os
import pathlib

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


# -------------------------------
# Main Application of Rocchio Classifier
if __name__ == "__main__":

    # Build Index and Vocab for all the documents in the federalist-papers including all the authors and disputed
    # documents
    corpus_path = Path("federalist-papers-rocchio")
    corpus = DirectoryCorpus.load_text_directory(corpus_path, '.txt')
    num_docs = len(list(corpus_path.glob("*.txt")))
    index_path = corpus_path / "index"
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

    # now for all the terms in the vocab, calculate v(d) which is a normalized vector of wdt components and Ld as length
    centroids = {}
    # get vocab
    vocabulary = disk_index.vocabulary()
    vd = {}
    # For each term in the vocabulary find the wdt
    for term in vocabulary:
        postings = disk_index.get_postings(term=term)
        # print(f"Processing term: {term}, postings_length:{len(postings)}")
        for posting in postings:
            wdt = 1 + ln(posting.tftd)
            Ld = disk_index.get_doc_info(posting.doc_id, "Ld")
            # print(f"Processing term: {term}, doc_id:{posting.doc_id}")
            # Update the component for the document with normalized value wdt/Ld
            if posting.doc_id not in vd.keys():
                vd[posting.doc_id] = [wdt/Ld]
            else:
                vd[posting.doc_id].append(wdt/Ld)

    disputed_vds = {}
    jay_vds = {}
    madison_vds = {}
    hamilton_vds = {}

    # There are 82 items in the vd dictionary.
    print(f"Number of documents/ v(d) components in the whole corpus:{len(vd)}")
    print("V(d) of each document in the federalist directory:")
    for doc_id in vd.keys():
        filename = corpus.get_document(doc_id).title
        # print(f"Filename: {filename}, Doc_ID:{doc_id}, v(d): {vd.get(doc_id)}")

        # Segregate the v(d)s for each of 3 authors and disputed documents
        file_number = int(filename.split('_')[1])

        # disputed documents
        if (49 <= file_number <= 57) or (62 == file_number) or (63 == file_number):
            disputed_vds[doc_id] = vd.get(doc_id)

        # Jay documents
        if (2 <= file_number <= 5) or (64 == file_number):
            jay_vds[doc_id] = vd.get(doc_id)

        # Madison documents
        if (10 == file_number) or (14 == file_number) or (37 <= file_number <= 48) or (58 == file_number):
            madison_vds[doc_id] = vd.get(doc_id)

        # Hamilton documents
        hamilton_vds[doc_id] = vd.get(doc_id)

    print("Disputed documents with v(d): ")
    for doc_id in disputed_vds.keys():
        filename = corpus.get_document(doc_id).title
        print(f"Filename:{filename}, doc_id:{doc_id}, v(d): {disputed_vds.get(doc_id)}")
    #
    # print("Hamilton documents with v(d): ")
    # for doc_id in hamilton_vds.keys():
    #     filename = corpus.get_document(doc_id).title
    #     print(f"Filename:{filename}, doc_id:{doc_id}, v(d): {hamilton_vds.get(doc_id)}")
    #
    # print("Madison documents with v(d): ")
    # for doc_id in madison_vds.keys():
    #     filename = corpus.get_document(doc_id).title
    #     print(f"Filename:{filename}, doc_id:{doc_id}, v(d): {madison_vds.get(doc_id)}")
    #
    # print("Jay documents with v(d): ")
    # for doc_id in jay_vds.keys():
    #     filename = corpus.get_document(doc_id).title
    #     print(f"Filename:{filename}, doc_id:{doc_id}, v(d): {jay_vds.get(doc_id)}")

    # calculate 3 centroids for each of the authors
    authors = ['HAMILTON', 'JAY', 'MADISON']
    hamilton_centroid = []
    madison_centroid = []
    jay_centroid = []

    hamilton_dc = 51

    # Centroid for hamilton
    vds_list = []
    for vds in hamilton_vds.values():
        # first document's vd values
        vds_list.append(vds)
    hamilton_centroid = [sum(i) for i in zip(*vds_list)]

    for i in range(0, len(hamilton_centroid)):
        hamilton_centroid[i] = hamilton_centroid[i] / hamilton_dc
    print(f"Hamilton Centroid: {hamilton_centroid}")

    first_disputed_document = disputed_vds[2]
    print(f"Length of first_disputed_document:{len(first_disputed_document)}")
    print(f"Length of hamilton centroid:{len(hamilton_centroid)}")

    distance = 0
    for i in range(0, len(first_disputed_document)):
        first_value = hamilton_centroid[i]
        second_value = first_disputed_document[i]
        # Subtract the values
        difference = first_value - second_value

        # square the difference
        squared_difference = difference ** 2

        # add it to the final result
        distance += squared_difference
    distance = sqrt(distance)
    print(f"Dist of hamilton to first disputed document: {distance}")
    # Find the centroid by dividing each term with total number of docs for that author
    # centroid = {}
    # for term in vd.keys():
    #     centroid[term] = vd.get(term) / index.num_docs
    #     centroids[author.lower()] = centroid
    #
    #     print(f"Author: {author}, Centroid: {centroids[author.lower()]}\n")
    #
    # # the first 30 components (alphabetically) of the normalized vector for the document
    #
    # # find euclidian distance for the disputed document from each author/class
    # distances = {}
    # for author in centroids.keys():
    #     distance = 0.
    #     for key, value in vd_disputed.items():
    #         # Get the first value for the term from the centroid
    #         centroid = centroids[author.lower()]
    #         if not centroid.get(key):
    #             first_value = 0
    #         else:
    #             first_value = centroid.get(key)
    #         # Get the second value for the term from the v(d) of disputed document
    #         second_value = value
    #
    #         # Subtract the values
    #         difference = first_value - second_value
    #
    #         # square the difference
    #         squared_difference = difference ** 2
    #
    #         # add it to the final result
    #         distance += squared_difference
    #     distance = sqrt(distance)
    #     distances[author.lower()] = distance
    #
    # for author in distances:
    #     print(f"\nAuthor: {author.lower()}, Euclidian Distance:{distances[author.lower()]}\n")
    #
    # # Find the smallest distance and classify the disputed document for that author
    # correct_author = min(distances, key=distances.get)
    # # disputed_document = disputed_corpus_path.glob("*.txt")
    # files = os.listdir(disputed_corpus_path)
    # disputed_document = [i for i in files if i.endswith('.txt')]
    # print(f"\nDisputed document {disputed_document} belongs to the author: {correct_author}\n")
