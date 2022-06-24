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
from numpy import log as ln, zeros
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
# Main Application of Naive Bayes Classifier
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

        positional_index, _, _, _, _, _ = index_corpus(corpus)
        
        if not index_path.is_dir():
            index_path.mkdir()
        index_writer = DiskIndexWriter(index_path)
        if not index_writer.posting_path.is_file():
            index_writer.write_index(positional_index)

        disk_index = DiskPositionalIndex(index_writer, num_docs=num_docs)
        author_index[author.lower()] = disk_index
        #print(f"{author} completed...")

    # PART A Find T*
    print("Top 10 terms:")
    top_terms = select_features(author_index.values())
    for score_term in top_terms:
        score, term = score_term
        print(f"Score: {score}, Term: {term}")

    # PART B Training Prior Conditional Probability Calculation
    # DENOMINATOR STORED IN ft_classes for each classes
    author_idxs = {}
    size_top_terms = len(top_terms)
    ft_classes = zeros(len(authors)) # Store ftc in T* for each class
    for score_term in top_terms:
        _, term = score_term
        idx = 0
        for author, index in author_index.items():
            # A list of postings
            postings = index.get_postings(term)
            dft = len(postings)
            ft_classes[idx] += dft
            author_idxs[author] = idx
            idx += 1
    ft_classes += size_top_terms

    # NUMERATOR
    for author, index in author_index.items():
        numerator = 0 # Stores ftc + 1 for each class
        # Vocab for each author
        vocab = index.vocabulary()
        for term in vocab:
            postings = index.get_postings(term)
            dft








    # term = 'abound'
    # #tp = NewTokenProcessor()
    # #term = tp.process_token(term)
    # for author, disk_index in author_index.items():
    #     print(f"Number of docs in {author}: {disk_index.num_docs}")
    #     print(f"dft for term = '{term}':")
    #     posting = disk_index.get_positional_postings(term)
    #     if posting:
    #         for post in posting:
    #             print(post)
    #         print(len(posting))


