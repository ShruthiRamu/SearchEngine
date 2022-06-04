import unittest
from pathlib import Path

from text.newtokenprocessor import NewTokenProcessor
from textmain import index_corpus
from documents import DocumentCorpus, DirectoryCorpus
from queries import BooleanQueryParser


class TestSearchEngine(unittest.TestCase):
    maxDiff = None

    def setUp(self):
        """self.petdict = {'cat': (('pets1', [1]), ('pets3', [3])),
                        'jump': [('pets1', [2]), ('pets4', [5])],
                        'high': [('pbts1', [3])],
                        'dog': [('pets2', [1]), ('pets3', [1])],
                        'run': [('pets2', [2]), ('pets4', [3])],
                        'fast': [('pets2', [3])],
                        'and': [('pets3', [2]), ('pets4', [4, 6])],
                        'are': [('pets3', [4])],
                        'pet': [('pets3', [5]), ('pets4', [1]), ('pets5', [1, 4])],
                        'should': [('pets4', [2]), ('pets5', [2])],
                        'play': [('pets4', [7])],
                        'have': [('pets5', [3])]
                        }"""
        self.petdict = {'cat': ((0, [1]), (2, [3])),
                        'jump': [(0, [2]), (3, [5])],
                        'high': [(0, [3])],
                        'dog': [(1, [1]), (2, [1])],
                        'run': [(1, [2]), (3, [3])],
                        'fast': [(1, [3])],
                        'and': [(2, [2]), (3, [4, 6])],
                        'are': [(2, [4])],
                        'pet': [(2, [5]), (3, [1]), (4, [1, 4]), (5, [1])],
                        'should': [(3, [2]), (4, [2]), (5, [2])],
                        'play': [(3, [7]), (4, [3])],
                        'have': [(4, [3])],
                        'game': [(5, [4])]
                        }
        self.token_processor = NewTokenProcessor()
        self.booleanqueryparser = BooleanQueryParser()
        self.corpus = DirectoryCorpus.load_text_directory(Path('utf_corpus'), ".txt")
        self.index = index_corpus(self.corpus)

    def test_pii1(self):
        self.assertEqual(self.index.get_postings('high')[0].positions, self.petdict['high'][0][1])

    def test_pii2(self):
        self.assertEqual(self.index.get_postings('and')[1].positions, self.petdict['and'][1][1])

    def test_pii3(self):
        self.assertEqual(self.index.get_postings('pet')[2].positions, self.petdict['pet'][2][1])

    def test_phrase(self):
        querycomponent = self.booleanqueryparser.parse_query(query='"pets should play"')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 1)
    def test_phrase2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='"pets should"')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 3)
    def test_and(self):
        querycomponent = self.booleanqueryparser.parse_query(query='pets should play')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 2)
    def test_and2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cat run')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 0)
    def test_or(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cats + dog + pet')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 6)
    def test_or2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='should + run + and')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 5)
    def test_not(self):
        querycomponent = self.booleanqueryparser.parse_query(query='-cats')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 4)
    def test_mix(self):
        querycomponent = self.booleanqueryparser.parse_query(query='should run + dogs')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 3)
    def test_mix2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cat + pets -dogs')
        postings = querycomponent.get_postings(self.index, token_processor=self.token_processor)
        self.assertTrue(len(postings) == 4)



if __name__ == '__main__':
    unittest.main()
