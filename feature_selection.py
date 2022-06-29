from indexes.index import Index
from heapq import nlargest
from math import isnan
from numpy import array, sum, zeros, log2
from typing import List
import itertools


def mutual_info(matrix, N):
    # Assuming matrix is 2-Dimensional (Terms on rows & Classes on columns)
    col_sum = sum(matrix, axis=0)
    row_sum = sum(matrix, axis=1)
    denominator_matrix = zeros(matrix.shape)
    for i, cs in enumerate(col_sum):
        denominator_matrix[:, i] = cs * row_sum
    numerator_matrix = N * matrix
    log_matrix = log2(numerator_matrix / denominator_matrix)
    return sum(matrix * log_matrix) / N


def select_features(indexes: List[Index], K):
    N = 0 # Total number of documents in all three indexes 
    vocab = []
    for index in indexes:
        vocab.append(index.vocabulary())
        N += index.num_docs
    print(f"Total number of documents: {N}")
    vocab = set(itertools.chain.from_iterable(vocab))
    term_score = {}
    neal_terms = ['upon', 'although', 'wish', 'whilst', 'lie', 'intend', 'kind', 'constitut', 'trial', 'gentlemen']
    for term in vocab:
        # Stores number of documents existing in each class
        term_exists = [] # Hamilton Jay Madison
        # Stores number of documents without the term in each class
        term_not_exists = [] # Hamilton Jay Madison

        for index in indexes:
            postings = index.get_postings(term)
            dft = len(postings)
            term_exists.append(dft)
            term_not_exists.append(index.num_docs - dft)
            term_class_matrix = array([term_exists, term_not_exists], dtype='float64')
            ict_score = mutual_info(term_class_matrix, N)
            if not isnan(ict_score):
                ict_score = max(ict_score, term_score.get(term, -999999))
            else:
                ict_score = 0
            term_score[term] = ict_score

    for term in neal_terms:
        print(f"Term: {term}, ict score: {term_score[term]}")

    return nlargest(K, [(score, term) for term, score in term_score.items()])    

# N = 801_948
# term_exist = [49, 27_652]
# term_notexist = [141, 774_106]
#
# matrix = array([term_exist, term_notexist], dtype='float64')
# print(matrix)
# score = mutual_info(matrix, N)
# print(f"Final Score: {score}")

# col_sum = sum(matrix, axis=0)
# print("Columns: ", col_sum)
# row_sum = sum(matrix, axis=1)
# print("Rows: ", row_sum)
# denominator_matrix = zeros(matrix.shape)
# for i, cs in enumerate(col_sum):
#     print("cs: ", cs)
#     print("result: ", cs*row_sum)
#     denominator_matrix[:, i] = cs * row_sum 
# print("Denominator matrix:")
# print(denominator_matrix)
# print("Numerator matrix:")
# numerator_matrix = N * matrix 
# print(numerator_matrix)
# log_matrix = log2(numerator_matrix/denominator_matrix)
# print("Log matrix:")
# print(log_matrix)
# print("matrix * log")
# print((matrix/N)*log_matrix)
# ict = sum(matrix*log_matrix) / N
# print(f"The final score is: {ict}")
# ==================================================
# print("*"*80)
# N = 42
# term_exist = [0, 0, 6]
# term_notexist = [10, 14, 12]
# matrix = array([term_exist, term_notexist], dtype='float64')
# print(matrix)


# col_sum = sum(matrix, axis=0)
# print("Columns: ", col_sum)
# row_sum = sum(matrix, axis=1)
# print("Rows: ", row_sum)
# denominator_matrix = zeros(matrix.shape)
# for i, cs in enumerate(col_sum):
#     print("cs: ", cs)
#     print("result: ", cs*row_sum)
#     denominator_matrix[:, i] = cs * row_sum 
# print("Denominator matrix:")
# print(denominator_matrix)
# print("Numerator matrix:")
# numerator_matrix = N * matrix 
# print(numerator_matrix)
# log_matrix = log2(numerator_matrix/denominator_matrix)
# print("Log matrix:")
# print(log_matrix)
# print("matrix * log")
# print((matrix/N)*log_matrix)
# ict = sum(matrix*log_matrix) / N
# print(f"The final score is: {ict}")