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

        # Author Processing
        author = d.get_author()
        if author:
            author = author.split(" ")
            for token in author:
                # Author in Index
                name = token_processor.process_token(token)
                index.add_term(name, d.id)
                code = soundex_code(name, encoding)
                soundex_index.add_term(code, name)
    return index, soundex_index


if __name__ == "__main__":
    corpus_path = Path.cwd() / 'mlb-articles-4000'
    corpus = DirectoryCorpus.load_json_directory(corpus_path, ".json")
    index, soundex_index = index_corpus(corpus)

    # Colliding Hash Code
    # C000 => ['cahill', 'cj']
    # J500 => ['jane', 'jim']
    # S360 => ['stier', 'star']
    # Z520 => ['zahneis', 'zinkie']

    print("\n====================================================")
    encoding = get_encoding()
    query = "zinkie"
    code = soundex_code(query, encoding)
    authors = soundex_index.get_postings(code)
    postings = [index.get_postings(author) for author in authors]
    print("Matches:")
    for a, posting in zip(authors, postings):
        doc_ids = [p.doc_id for p in posting]
        print(f"Author: {a.capitalize()} => Document(s): {doc_ids}")