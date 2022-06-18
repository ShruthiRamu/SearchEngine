import abc
from math import sqrt

from numpy import log as ln

from queries import TermLiteral
from text.newtokenprocessor import NewTokenProcessor


class RankedStrategy:
    """
    Define the interface of interest to clients.
    Maintain a reference to a Strategy object.
    """

    def __init__(self, strategy):
        self._strategy = strategy

    def calculate(self, query, disk_index, corpus_size) -> {}:
        return self._strategy.calculate(self, query=query, disk_index=disk_index, corpus_size=corpus_size)


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

    def calculate(self, query, disk_index, corpus_size) -> {}:
        # accumulator = {}
        # N = len(document_weights)
        #
        # for term in set(query.split(" ")):
        #     postings = disk_index.get_postings(term)
        #     dft = len(postings)
        #     wqt = ln(1 + N / dft)
        #
        #     for posting in postings:
        #         wdt = 1 + ln(posting.tftd)
        #         if posting.doc_id not in accumulator.keys():
        #             accumulator[posting.doc_id] = 0.
        #         accumulator[posting.doc_id] += (wdt * wqt)
        #
        # for doc_id, accum in accumulator.items():
        #     Ld = disk_index.get_doc_weight(doc_id)
        #     accum /= Ld

        accumulator = {}
        N = corpus_size
        token_processor = NewTokenProcessor()
        for term in set(query.split(" ")):
            tokenized_term = TermLiteral(term, False)
            postings = tokenized_term.get_postings(disk_index, token_processor=token_processor)
            # postings = disk_index.get_postings(term)
            dft = len(postings)
            wqt = ln(1 + N / dft)

            for posting in postings:
                wdt = 1 + ln(posting.tftd)
                if posting.doc_id not in accumulator.keys():
                    accumulator[posting.doc_id] = 0.
                accumulator[posting.doc_id] += (wdt * wqt)

        for doc_id in accumulator.keys():
            Ld = disk_index.get_doc_info(doc_id, "Ld")
            accumulator[doc_id] /= Ld

        return accumulator


class TraditionalStrategy(IRankedStrategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def calculate(self, query, disk_index, corpus_size) -> {}:
        accumulator = {}
        N = corpus_size
        token_processor = NewTokenProcessor()

        for term in set(query.split(" ")):
            tokenized_term = TermLiteral(term, False)
            postings = tokenized_term.get_postings(disk_index, token_processor=token_processor)
            dft = len(postings)
            wqt = ln(N / dft)

            for posting in postings:
                wdt = posting.tftd
                if posting.doc_id not in accumulator.keys():
                    accumulator[posting.doc_id] = 0.
                accumulator[posting.doc_id] += (wdt * wqt)

        for doc_id in accumulator.keys():
            Ld = disk_index.get_doc_info(doc_id, "Ld")
            accumulator[doc_id] /= Ld

        return accumulator


class OkapiBM25Strategy(IRankedStrategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def calculate(self, query, disk_index, corpus_size) -> {}:
        accumulator = {}
        N = corpus_size
        token_processor = NewTokenProcessor()

        for term in set(query.split(" ")):
            tokenized_term = TermLiteral(term, False)
            postings = tokenized_term.get_postings(disk_index, token_processor=token_processor)
            dft = len(postings)
            wqt = max(0.1, ln((N - dft + 0.5) / (dft + 0.5)))

            for posting in postings:
                docLength = disk_index.get_doc_info(posting.doc_id, "docLength")
                doc_tokens_len_avg = disk_index.get_avg_tokens_corpus()
                wdt = (2.2 * posting.tftd) / \
                      ((1.2 * (0.25 + (
                              0.75 * (docLength / doc_tokens_len_avg)))) + posting.tftd)
                if posting.doc_id not in accumulator.keys():
                    accumulator[posting.doc_id] = 0.
                accumulator[posting.doc_id] += (wdt * wqt)

        for doc_id in accumulator.keys():
            Ld = 1
            accumulator[doc_id] /= Ld

        return accumulator


class WackyStrategy(IRankedStrategy):
    """
    Implement the algorithm using the Strategy interface.
    """

    def calculate(self, query, disk_index, corpus_size) -> {}:
        accumulator = {}
        N = corpus_size
        token_processor = NewTokenProcessor()
        for term in set(query.split(" ")):
            tokenized_term = TermLiteral(term, False)
            postings = tokenized_term.get_postings(disk_index, token_processor=token_processor)
            dft = len(postings)
            wqt = max(0, ln((N - dft) / dft))

            for posting in postings:
                average_tftd = disk_index.get_doc_info(posting.doc_id, "avg_tftd")
                wdt = (1 + ln(posting.tftd)) / (1 + ln(average_tftd))
                if posting.doc_id not in accumulator.keys():
                    accumulator[posting.doc_id] = 0.
                accumulator[posting.doc_id] += (wdt * wqt)

        for doc_id in accumulator.keys():
            byte_size = disk_index.get_doc_info(doc_id, "byte_size")
            Ld = sqrt(byte_size)
            accumulator[doc_id] /= Ld

        return accumulator
