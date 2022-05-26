from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index
from indexes.invertedindex import InvertedIndex
from text.basictokenprocessor import BasicTokenProcessor
from text.englishtokenstream import EnglishTokenStream

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""

def index_corpus(corpus: DocumentCorpus) -> Index:
    token_processor = BasicTokenProcessor()
    index = InvertedIndex()
    # Iterate through the documents in the corpus:
    for d in corpus:
        # Tokenize each document's content,
        stream = EnglishTokenStream(d.get_content())
        for token in stream:
            # Process each token.
            term = token_processor.process_token(token)
            # Add each processed term to the index with .add_term().
            index.add_term(term=term, doc_id=d.id)
    return index


if __name__ == "__main__":
    corpus_path = Path()
    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(d)

    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.
    query = "whale"  # hard-coded search for "whale"
    for p in index.get_postings(query):
        print(f"Document ID {p.doc_id}")

    # TODO: fix this application so the user is asked for a term to search.
