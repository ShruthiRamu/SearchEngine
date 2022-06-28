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
from numpy import log as ln, zeros, log10, argmax, log2
from math import sqrt
from pathlib import Path
import warnings

#ignore by message
warnings.filterwarnings("ignore", message="divide by zero encountered in log2")
warnings.filterwarnings("ignore", message="invalid value encountered in multiply")
warnings.filterwarnings("ignore", message="invalid value encountered in true_divide")



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
    #document_tokens_length_average = document_tokens_length_total / len(corpus)
    document_tokens_length_average = []
    return index, document_weights, document_tokens_length_per_document, byte_size_ds, average_tftds, document_tokens_length_average


# -------------------------------
# Main Application of Naive Bayes Classifier
if __name__ == "__main__":

    authors = ['HAMILTON', 'JAY', 'MADISON'] # LABELS
    author_index = {} # Maps authors to their disk index
    corpus_dir = Path('federalist_papers_nb')
    N = 0 # Number of all documents in all three classes
    # Build three separate indexes for 3 classes
    for author in authors:
        corpus_path = corpus_dir / author
        corpus = DirectoryCorpus.load_text_directory(corpus_path, '.txt')
        num_docs = len(list(corpus_path.glob("*.txt")))
        N += num_docs
        index_path = corpus_path / (author.lower() + "_index")
        index_path = index_path.resolve()

        positional_index = index_corpus(corpus)[0]
        
        if not index_path.is_dir():
            print("Making a new directory")
            index_path.mkdir()
        index_writer = DiskIndexWriter(index_path)
        if not index_writer.posting_path.is_file():
            index_writer.write_index(positional_index)

        disk_index = DiskPositionalIndex(index_writer, num_docs)
        author_index[author.lower()] = disk_index
        #print(f"{author} completed...")

    # PART A Find T*
    num_terms = 10
    print(f"Top {num_terms} terms by I(T, C), and giving a score of 0 to any I(T,C) that is NaN:")
    top_terms = select_features(author_index.values(), 50)
    for score_term in top_terms[:num_terms]:
        score, term = score_term
        print(f"Score: {score}, Term: {term}")

    # PART B Training Prior Conditional Probability Calculation
    # DENOMINATOR STORED IN ft_classes for each classes
    author_idxs = {}
    size_top_terms = len(top_terms) # |T*|
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
    ft_classes += size_top_terms # Same for all authors

    # NOTE: Calculate P(C) = Nc / N
    prob_classes = zeros(len(authors)) # Stores P(C) for each authors
    author_priors = {}
    # NUMERATOR
    for author, index in author_index.items():
        prob_classes[author_idxs[author]] = index.num_docs / N # for next step

        # Vocab for each author
        vocab = index.vocabulary()
        numerators = zeros(len(vocab)) # Stores ftc + 1 for each term in an author vocab
        for i, term in enumerate(vocab):
            postings = index.get_postings(term)
            dft = len(postings)
            ftc = dft + 1
            numerators[i] = ftc
        priors = numerators / ft_classes[author_idxs[author]]
        author_priors[author] = priors

        prob_path = index.disk_index_writer.index_path / "priors.txt"
        with open(prob_path, 'w') as f:
            f.write("\n".join(str(prior) for prior in priors))

    # PART C: Classification
    disputed_path = corpus_dir / "DISPUTED"
    disputed_docs = DirectoryCorpus.load_text_directory(disputed_path, ".txt")
    num_disputed_docs = len(list(disputed_path.glob("*.txt")))
    #print(f"No. of disputed docs: {num_disputed_docs}")
    diff_terms = [score_term[1] for score_term in top_terms] # T* as a list
    # Each row of the matrix is the author
    # Each column of the matrix is the document in the disputed folder
    # Matrix stores the cd without the argmax
    authors_docs_cds = zeros(shape=(len(authors), num_disputed_docs))
    token_processor = NewTokenProcessor()
    for author, index in author_index.items():
        P_c = log10(prob_classes[author_idxs[author]])
        row = author_idxs[author]
        priors = author_priors[author]
        vocab = index.vocabulary()
        for doc in disputed_docs:
            prior_sums = 0
            stream = EnglishTokenStream(doc.get_content())
            for token in stream:
                terms = token_processor.process_token(token)
                for term in terms:
                    if term in diff_terms:
                        try:
                            ith_term = vocab.index(term) # Actual index in list
                            prior = priors[ith_term]
                            prior_sums += log10(prior)
                        except ValueError:
                            print("here")
                            prior_sums += (1 / size_top_terms)
            cd = P_c + prior_sums
            authors_docs_cds[row, doc.id] = cd

    idx_authors = dict([(value, key) for key, value in author_idxs.items()])

    # Find cds by taking the argmax
    author_ids = argmax(authors_docs_cds, axis=0)
    paper_49_doc_id = -1
    print("\nClassification")
    for doc_id, author_id in enumerate(author_ids):
        if disputed_docs.get_document(doc_id).title == "paper_49":
            paper_49_doc_id = doc_id
        print(f"Document: {disputed_docs.get_document(doc_id).title}, Author: {idx_authors[author_id].capitalize()}")

    print("\nBayes score for paper 49")
    bayes_scores = authors_docs_cds[:, paper_49_doc_id]
    for i, bayes_score in enumerate(bayes_scores):
        print(f"Author: {idx_authors[i].capitalize()}, Score: {bayes_score}")

    print("\nAuthor Score Matrix: ")
    print(authors_docs_cds)






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


