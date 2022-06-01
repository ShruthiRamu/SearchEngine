import unittest
from pathlib import Path

from BooleanQueryIndexer import index_corpus
from documents import DocumentCorpus, DirectoryCorpus
from queries import BooleanQueryParser


class TestSearchEngine(unittest.TestCase):

    def setUp(self):
        self.petdict = {'cats': (('pets1', [1]), ('pets3', [3])),
                        'jump': [('pets1', [2]), ('pets4', [5])],
                        'high': [('pbts1', [3])],
                        'dogs': [('pets2', [1]), ('pets3', [1])],
                        'run': [('pets2', [2]), ('pets4', [3])],
                        'fast': [('pets2', [3])],
                        'and': [('pets3', [2]), ('pets4', [4, 6])],
                        'are': [('pets3', [4])],
                        'pets': [('pets3', [5]), ('pets4', [1]), ('pets5', [1, 4])],
                        'should': [('pets4', [2]), ('pets5', [2])],
                        'play': [('pets4', [7])],
                        'have': [('pets5', [3])]
                        }
        self.corpus = DirectoryCorpus.load_text_directory(Path('utf_corpus'), ".txt")
        self.index = index_corpus(self.corpus)

    def test_pii1(self):
        self.assertEqual(self.index.get_postings('high')[0].positions, self.petdict['high'][0][1])

    def test_pii2(self):
        self.assertEqual(self.index.get_postings('and')[1].positions, self.petdict['and'][1][1])

    def test_pii3(self):
        self.assertEqual(self.index.get_postings('pets')[2].positions, self.petdict['pets'][2][1])

    def test_phrase(self):
        booleanqueryparser = BooleanQueryParser()
        querycomponent = booleanqueryparser.parse_query(query="'jump high'")
        self.assertEqual(querycomponent.get_postings(self.index)[0].doc_id, 0)


if __name__ == '__main__':
    unittest.main()
