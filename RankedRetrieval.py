class Posting:
    def __init__(self, doc_id : int, position=-1):
        self.doc_id = doc_id
        self.positions = [] if position == -1 else position

    def __str__(self):
        if self.positions:
            return f"(ID: {self.doc_id }, -> {[pos for pos in self.positions]})"
        return str(self.doc_id)

index = {
    "angels": [
        Posting(2, [36, 174, 252, 651]), Posting(4, [12, 22, 102, 432]), Posting(7, [17]), Posting(9, [1, 3])
    ],
    "dog": [
        Posting(2, [999]),
    ],
    "win": [
      Posting(2, [652]), Posting(8, [17])
    ],
    "god": [
        Posting(2, [4, 170, 652]), Posting(5, [9]), Posting(7, [18])
    ],

    "buffoon": [
        Posting(2, [653, 999]), Posting(5, [10])
    ],
    "fools": [
        Posting(2, [1, 17, 74, 222]), Posting(4, [8, 78, 108, 458]), Posting(7, [3, 13, 23, 193])
    ],
    "fear": [
        Posting(2, [87, 704, 722, 901]), Posting(4, [13, 43, 113, 433]), Posting(7, [18, 328, 528]), Posting(9, [2])
    ],
    "in": [
        Posting(2, [3, 37, 76, 444, 851]), Posting(4, [10, 20, 110, 470, 500]), Posting(7, [5, 15, 25, 195])
    ],
    "rush": [
        Posting(2, [2, 66, 194, 321, 702]), Posting(4, [9, 69, 149, 429, 569]), Posting(7, [4, 14, 104])
    ],
    "to": [
        Posting(2, [47, 86, 234, 999]), Posting(4, [14, 24, 774, 944]), Posting(7, [199, 319, 599, 709])
    ],
    "tread": [
        Posting(2, [57, 94, 333]), Posting(4, [15, 35, 155]), Posting(7, [20, 320])
    ],
    "computers":[Posting(10, [1, 4, 5])],
    "there": [Posting(10, [2])],
    "no": [Posting(10, [3])],
}

from numpy import log as ln
from heapq import nlargest
query = "fools rush in"



accumulator = {}
N = 10 # Corpus Size TO BE UPDATED
L = len(index.keys()) # TO BE UPDATED
# Distinct terms in query
for term in set(query.split(" ")):
    dft = len(index[term])
    wqt = ln(1+N/dft)
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