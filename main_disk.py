from pathlib import Path
from diskindexwriter import DiskIndexWriter
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.invertedindex import InvertedIndex
from indexes.positionalinvertedindex import PositionalInvertedIndex
from queries import BooleanQueryParser, PhraseLiteral
from text.englishtokenstream import EnglishTokenStream
from time import time_ns
from text.newtokenprocessor import NewTokenProcessor


def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = NewTokenProcessor()
    # token_processor = BasicTokenProcessor()
    index = PositionalInvertedIndex()
    document_wegihts = [] # Ld for all documents in corpus
    for d in corpus:

        stream = EnglishTokenStream(d.get_content())
        position = 1
        for token in stream:
            terms = token_processor.process_token(token)
            for term in terms:
                index.add_term(term=term, position=position, doc_id=d.id)
            position += 1
    return index


" Main Application of Search Engine "

if __name__ == "__main__":

    #corpus_path = Path('dummytextfiles')
    corpus_path = Path('dummytextfiles')
    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(d)

    index_writer = DiskIndexWriter()
    index_path = Path('dummytextfiles/index/postings.bin')
    print("Index path: ", index_path)
    index_writer.write_index(index, index_path)
    print("Term -> Byte Position Mapping: ")
    print(index_writer.b_tree)
