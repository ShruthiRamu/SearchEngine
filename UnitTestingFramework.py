import unittest
from pathlib import Path

from PositionalInvertedIndexer import index_corpus
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream


class TestSearchEngine(unittest.TestCase):

    def test_pii(self):
        petdict = {'cats': (('pets1', [1]), ('pets3', [3])),
                   'jump': (('pets1', [2]), ('pets4', [5])),
                   'high': (('pets1', [3])),
                   'dogs': (('pets2', [1]), ('pets3', [1])),
                   'run': (('pets2', [2]), ('pets4', [3])),
                   'fast': (('pets2', [3])),
                   'and': (('pets3', [2]), ('pets4', [4, 6])),
                   'are': (('pets3', [4])),
                   'pets': (('pets3', [5]), ('pets4', [1]), ('pets5', [1, 4])),
                   'should': (('pets4', [2]), ('pets5', [2])),
                   'play': (('pets4', [7])),
                   'have': (('pets5', [3]))
                   }
        corpus = DirectoryCorpus.load_text_directory(Path('utf_corpus'), ".txt")
        index = index_corpus(corpus)
        self.assertEqual(index.__dict__, petdict)


if __name__ == '__main__':
    unittest.main()