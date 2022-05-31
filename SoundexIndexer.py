from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.invertedindex import InvertedIndex
from indexes.soundexindex import SoundexIndex
from soundexcode import get_encoding, soundex_code
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

""" This basic program builds a Soundex Index over json files to search the authors with similar sounding names """
def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    index = InvertedIndex()
    soundex_index = SoundexIndex()

    # Soundex Letter -> Digit Mapping
    encoding = get_encoding()

    # Iterate through the documents in the corpus:
    for d in corpus:
        # Tokenize each document's content,
        stream = EnglishTokenStream(d.get_content())
        for token in stream:
            # Process each token.
            term = token_processor.process_token(token)
            index.add_term(term, d.id)

        #code = soundex_code(term, encoding)
        #soundex_index.add_term(code, term)

        # Process author first and last name
        # Get soundex code for each term
        # code = soundex_code(name, encoding)
        # soundexindex.addterm(term=code, doc_id=d.id)
        # Returns two indexes?
    return index, soundex_index


if __name__ == "__main__":
    corpus_path = Path()
    corpus = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(corpus)
