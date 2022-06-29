import os

from diskindexwriter import DiskIndexWriter
from documents.corpus import DocumentCorpus
from documents.directorycorpus import DirectoryCorpus
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

    authors = ['HAMILTON', 'JAY', 'MADISON']
    author_index = {}
    corpus_dir = Path('federalist-papers')
    # Three separate indexes for 3 classes
    for author in authors:
        corpus_path = corpus_dir / author
        corpus = DirectoryCorpus.load_text_directory(corpus_path, '.txt')
        num_docs = len(list(corpus_path.glob("*.txt")))
        index_path = corpus_path / (author.lower() + "_index")
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
        author_index[author.lower()] = disk_index
        # print(f"{author} completed...")

    centroids = {}
    for author, index in author_index.items():
        # get vocab for each author/class
        vocabulary = index.vocabulary()
        vd = {}
        # For each term in the vocabulary find the wdt
        for term in vocabulary:
            postings = index.get_postings(term=term)
            for posting in postings:
                wdt = 1 + ln(posting.tftd)
                Ld = index.get_doc_info(posting.doc_id, "Ld")
                # Update the components(wdt) for the term
                if term not in vd.keys():
                    vd[term] = wdt / Ld
                else:
                    # if term already present then add it to the sum for the final centroid calculation
                    vd[term] += wdt / Ld
        # Find the centroid by dividing each term with total number of docs for that author
        centroid = {}
        for term in vd.keys():
            centroid[term] = vd.get(term) / index.num_docs
            centroids[author.lower()] = centroid

        # print(f"Author: {author}, Centroid: {centroids[author.lower()]}\n")

    # Classify each disputed document
    disputed_documents_dir = Path("rocchio-disputed")
    disputed_papers = ['paper_49', 'paper_50', 'paper_51', 'paper_52', 'paper_53', 'paper_54', 'paper_55', 'paper_56',
                       'paper_57', 'paper_62', 'paper_63']
    # For each paper in the disputed directory
    for paper in disputed_papers:
        # Create v(d) for disputed documents
        disputed_corpus_path = disputed_documents_dir / paper
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
                # Update the normalized vector components for the term with wdt/Ld
                vd_disputed[term] = wdt / Ld

        # the first 30 components (alphabetically) of the normalized vector for the document
        print(
            f"The first 30 components (alphabetically) of the normalized vector for the document{paper}:{list(vd_disputed.items())[:30]}\n")

        # find euclidian distance for the disputed document from each author/class
        distances = {}
        for author in centroids.keys():
            distance = 0.
            for key, value in vd_disputed.items():
                # Get the first value for the term from the centroid
                centroid = centroids[author.lower()]
                if not centroid.get(key):
                    first_value = 0
                else:
                    first_value = centroid.get(key)
                # Get the second value for the term from the v(d) of disputed document
                second_value = value

                # Subtract the values
                difference = first_value - second_value

                # square the difference
                squared_difference = difference ** 2

                # add it to the final result

                distance += squared_difference
            distance = sqrt(distance)
            distances[author.lower()] = distance

        for author in distances:
            print(f"Author: {author.lower()}, Euclidian Distance:{distances[author.lower()]}")

        # Find the smallest distance and classify the disputed document for that author
        correct_author = min(distances, key=distances.get)

        # disputed_document = disputed_corpus_path.glob("*.txt")
        # files = os.listdir(disputed_corpus_path)
        # disputed_document = [i for i in files if i.endswith('.txt')]
        print(f"Disputed document {paper} belongs to the author: {correct_author}\n")
