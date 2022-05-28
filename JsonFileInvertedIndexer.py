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
    # TODO: Need to add the json files to the repository
    corpus_path = Path('all-nps-sites-extracted')
    d = DirectoryCorpus.load_json_directory(corpus_path, ".json")

    # Build the index over this directory.
    index = index_corpus(d)

    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.

    while (True):
        print("Enter the term to search/ Enter 'quit' to exit: ")
        query = input()
        if query == 'quit':
            break
        # print(query)
        for p in index.get_postings(query):
            print(f"Document ID(title) : {d.get_document(p.doc_id).title}")