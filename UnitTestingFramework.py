import unittest
from pathlib import Path
from time import time_ns

import SoundexIndexer
from text.newtokenprocessor import NewTokenProcessor
from main import index_corpus
from documents import DocumentCorpus, DirectoryCorpus
from queries import BooleanQueryParser


class TestSearchEngine(unittest.TestCase):
    maxDiff = None

    def setUp(self):
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

    def test_tokenizer(self):
        self.assertEqual(self.token_processor.process_token("!ad'am''anTIn'e#")[0], "adamantin")

    def test_tokenizer2(self):
        self.assertListEqual(self.token_processor.process_token("Hewlett-Packard"),
                             ['hewlettpackard', 'hewlett', 'packard'])

    def test_tokenizer3(self):
        self.assertListEqual(self.token_processor.process_token('-F""ree"-for-"all!'),
                             ['freeforal', 'free', 'for', 'all'])

    def test_pii1(self):
        self.assertEqual(self.index[0].get_postings('high')[0].positions, self.petdict['high'][0][1])

    def test_pii2(self):
        self.assertEqual(self.index[0].get_postings('jump')[0].positions, self.petdict['jump'][0][1])

    def test_pii3(self):
        self.assertEqual(self.index[0].get_postings('jump')[1].positions, self.petdict['jump'][1][1])

    def test_pii4(self):
        self.assertEqual(self.index[0].get_postings('play')[1].positions, self.petdict['play'][1][1])

    def test_pii5(self):
        self.assertEqual(self.index[0].get_postings('should')[2].positions, self.petdict['should'][2][1])

    def test_pii6(self):
        self.assertEqual(self.index[0].get_postings('pet')[3].positions, self.petdict['pet'][3][1])

    def test_pii7(self):
        self.assertEqual(self.index[0].get_postings('and')[1].positions, self.petdict['and'][1][1])

    def test_pii8(self):
        self.assertEqual(self.index[0].get_postings('pet')[2].positions, self.petdict['pet'][2][1])

    def test_phrase(self):
        querycomponent = self.booleanqueryparser.parse_query(query='"pets should play"')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 1)

    def test_phrase2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='"pets should run and jump and play"')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 1)

    def test_and(self):
        querycomponent = self.booleanqueryparser.parse_query(query='pets should play')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 2)

    def test_and2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cat run')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 0)

    def test_and3(self):
        querycomponent = self.booleanqueryparser.parse_query(query='pets should play run jump')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 1)

    def test_or(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cats + dog + pet')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 6)

    def test_or2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='should + run + and')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 5)

    def test_or3(self):
        querycomponent = self.booleanqueryparser.parse_query(query='rat + hamster + bird')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 0)

    def test_not(self):
        querycomponent = self.booleanqueryparser.parse_query(query='pets -should')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 1)

    def test_not2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='-run dogs')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 1)

    def test_not3(self):
        querycomponent = self.booleanqueryparser.parse_query(query='should -jump -run')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 2)

    def test_not4(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cat -jump -dog')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 0)

    def test_mix(self):
        querycomponent = self.booleanqueryparser.parse_query(query='should run + dogs')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 3)

    def test_mix2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cat + run -dogs')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 3)

    def test_mix3(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cat + should + fast + run -dogs')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 6)

    def test_mix4(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cat -dog -jump + dog -cat -fast + pets -should -are')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 0)

    def test_mix5(self):
        querycomponent = self.booleanqueryparser.parse_query(query='cat -dog -jump + dog -cat -fast + pets -should')
        postings = querycomponent.get_postings(self.index[0], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 1)

    def test_soundex(self):
        print("Soundex Indexing...")
        soundex_indexer_dir = 'mlb-articles-4000'
        corpus_path = Path(soundex_indexer_dir)
        soundex_corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        start = time_ns()
        self.i_index, self.soundex_index = SoundexIndexer.index_corpus(soundex_corpus)
        end = time_ns()
        print(f"Soundex Indexing Time: {(end - start) / 1e+9} secs\n")
        authors = SoundexIndexer.soundex_indexer(query='Bryan', index=self.i_index,
                                                 soundex_index=self.soundex_index)
        author_list = []
        for a in authors:
            author_list.append(a.__str__())
        print(author_list)
        self.assertTrue(author_list.__contains__("brian"))

    def test_soundex2(self):
        print("Soundex Indexing...")
        soundex_indexer_dir = 'mlb-articles-4000'
        corpus_path = Path(soundex_indexer_dir)
        soundex_corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        start = time_ns()
        self.i_index, self.soundex_index = SoundexIndexer.index_corpus(soundex_corpus)
        end = time_ns()
        print(f"Soundex Indexing Time: {(end - start) / 1e+9} secs\n")
        authors = SoundexIndexer.soundex_indexer(query='Richrd', index=self.i_index,
                                                 soundex_index=self.soundex_index)
        author_list = []
        for a in authors:
            author_list.append(a.__str__())
        print(author_list)
        self.assertTrue(author_list.__contains__("richard"))

    def test_soundex3(self):
        print("Soundex Indexing...")
        soundex_indexer_dir = 'mlb-articles-4000'
        corpus_path = Path(soundex_indexer_dir)
        soundex_corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        start = time_ns()
        self.i_index, self.soundex_index = SoundexIndexer.index_corpus(soundex_corpus)
        end = time_ns()
        print(f"Soundex Indexing Time: {(end - start) / 1e+9} secs\n")
        authors = SoundexIndexer.soundex_indexer(query='merican', index=self.i_index,
                                                 soundex_index=self.soundex_index)
        author_list = []
        for a in authors:
            author_list.append(a.__str__())
        print(author_list)
        self.assertTrue(author_list.__contains__("merkin"))

    def test_soundex4(self):
        print("Soundex Indexing...")
        soundex_indexer_dir = 'mlb-articles-4000'
        corpus_path = Path(soundex_indexer_dir)
        soundex_corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
        start = time_ns()
        self.i_index, self.soundex_index = SoundexIndexer.index_corpus(soundex_corpus)
        end = time_ns()
        print(f"Soundex Indexing Time: {(end - start) / 1e+9} secs\n")

        authors = SoundexIndexer.soundex_indexer(query='Berri', index=self.i_index,
                                                 soundex_index=self.soundex_index)
        author_list = []
        for a in authors:
            author_list.append(a.__str__())
        print(author_list)
        self.assertTrue(author_list.__contains__("berry") and author_list.__contains__("berra"))

    def test_biword(self):
        querycomponent = self.booleanqueryparser.parse_query(query='"pets should"')
        postings = querycomponent.get_postings(self.index[1], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 3)

    def test_biword2(self):
        querycomponent = self.booleanqueryparser.parse_query(query='"dogs run"')
        postings = querycomponent.get_postings(self.index[1], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 1)

    def test_biword3(self):
        querycomponent = self.booleanqueryparser.parse_query(query='"dogs run fast"')
        postings = querycomponent.get_postings(self.index[1], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 0)

    def test_biword4(self):
        querycomponent = self.booleanqueryparser.parse_query(query='"dogs"')
        postings = querycomponent.get_postings(self.index[1], token_processor=self.token_processor)
        self.assertTrue(len(postings) == 0)


if __name__ == '__main__':
    unittest.main()
