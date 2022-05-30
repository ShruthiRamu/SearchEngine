from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.positionalinvertedindex import PositionalInvertedIndex
from soundexcode import get_encoding, soundex_code
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""

def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    pindex = PositionalInvertedIndex()

    # Create Soundex Index
    # USE the InvertedIndex?

    # Get encoding
    # encoding = get_encoding()

    # Iterate through the documents in the corpus:
    for d in corpus:
        # Tokenize each document's content,
        stream = EnglishTokenStream(d.get_content())
        position = 1
        print(f"\nDoc ID: {d.id}")
        for token in stream:
            # Process each token.
            term = token_processor.process_token(token)
            print(f"Term: {term}, Position: {position}")
            pindex.add_term(term=term, position=position, doc_id=d.id)
            position += 1

        # Process author first and last name
        # Get soundex code for each term
        # code = soundex_code(name, encoding)
        # soundexindex.addterm(term=code, doc_id=d.id)
        # Returns two indexes?
    return pindex


if __name__ == "__main__":
    corpus_path = Path()
    corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(corpus)
