import abc
from math import sqrt

from numpy import log as ln


class RankedStrategy:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, strategy):
        self._strategy = strategy

    def calculate(self, query, disk_index, document_weights, document_token_length=None, byte_size_d=None, average_tftd=None,
                  document_tokens_length_average=None):
        self._strategy.calculate(self, query=query, disk_index=disk_index, document_weights=document_weights,
                                 document_token_length=document_token_length, byte_size_d=byte_size_d,
                                 average_tftd=average_tftd, document_tokens_length_average=document_tokens_length_average,)


class IRankedStrategy(metaclass=abc.ABCMeta):
    """
    Declare an interface common to all supported algorithms. RankedStrategy
    uses this interface to call the algorithm defined by a
    RankedStrategy.
    """

    @abc.abstractmethod
    def calculate(self, **kwargs) -> {}:
        pass


class DefaultStrategy(IRankedStrategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def calculate(self, query, disk_index, document_weights, **kwargs) -> {}:
        accumulator = {}
        N = len(document_weights)

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

        return accumulator


class TraditionalStrategy(IRankedStrategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def calculate(self, query, disk_index, document_weights, **kwargs) -> {}:
        accumulator = {}
        N = len(document_weights)

        for term in set(query.split(" ")):
            postings = disk_index.get_postings(term)
            dft = len(postings)
            wqt = ln(1 + N / dft)

            for posting in postings:
                wdt = posting.tftd
                if posting.doc_id not in accumulator.keys():
                    accumulator[posting.doc_id] = 0.
                accumulator[posting.doc_id] += (wdt * wqt)

        for doc_id, accum in accumulator.items():
            Ld = disk_index.get_doc_weight(doc_id)
            accum /= Ld

        return accumulator


class OkapiBM25Strategy(IRankedStrategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def calculate(self, query, disk_index, document_weights, document_token_length,
                  document_tokens_length_average, **kwargs) -> {}:
        accumulator = {}
        N = len(document_weights)

        for term in set(query.split(" ")):
            postings = disk_index.get_postings(term)
            dft = len(postings)
            wqt = max(0.1, ln((N - dft + 0.5) / (dft + 0.5)))

            for posting in postings:
                wdt = (2.2 * posting.tftd) / \
                      ((1.2 * (0.25 + (
                              0.75 * (document_token_length / document_tokens_length_average)))) + posting.tftd)
                if posting.doc_id not in accumulator.keys():
                    accumulator[posting.doc_id] = 0.
                accumulator[posting.doc_id] += (wdt * wqt)

        for doc_id, accum in accumulator.items():
            Ld = 1
            accum /= Ld

        return accumulator


class WackyStrategy(IRankedStrategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def calculate(self, query, disk_index, document_weights, average_tftd, byte_size_d, **kwargs) -> {}:
        accumulator = {}
        N = len(document_weights)

        for term in set(query.split(" ")):
            postings = disk_index.get_postings(term)
            dft = len(postings)
            wqt = max(0, ln((N - dft) / dft))

            for posting in postings:
                wdt = (1 + ln(posting.tftd)) / (1 + ln(average_tftd))
                if posting.doc_id not in accumulator.keys():
                    accumulator[posting.doc_id] = 0.
                accumulator[posting.doc_id] += (wdt * wqt)

        for doc_id, accum in accumulator.items():
            Ld = sqrt(byte_size_d)
            accum /= Ld

        return accumulator
