from pathlib import Path
from documents import DocumentCorpus, DirectoryCorpus
from indexes import Index, TermDocumentIndex
from text import BasicTokenProcessor, englishtokenstream

"""This basic program builds a term-document matrix over the .txt files in 
the same directory as this file."""

def index_corpus(corpus : DocumentCorpus) -> Index:
    
    token_processor = BasicTokenProcessor()
    vocabulary = set()
    
    for d in corpus:
        print(f"Found document {d.title}")
        DocumentToken = englishtokenstream.EnglishTokenStream(d.get_content())
        for i in DocumentToken:
            vocabulary.add(token_processor.process_token(i))
        # TODO:
        #   Tokenize the document's content by creating an EnglishTokenStream around the document's .content()
        #   Iterate through the token stream, processing each with token_processor's process_token method.
        #   Add the processed token (a "term") to the vocabulary set.

    tdi = TermDocumentIndex(vocabulary, len(corpus))
    for e in corpus:
        DocumentToken = englishtokenstream.EnglishTokenStream(e.get_content())
        for b in DocumentToken:
            token = token_processor.process_token(b)
            tdi.add_term(token, e.id)
            #print(counterID)

    return tdi
    # TODO:
    # After the above, next:
    # Create a TermDocumentIndex object, with the vocabular you found, and the len() of the corpus.
    # Iterate through the documents in the corpus:
    #   Tokenize each document's content, again.
    #   Process each token.
    #   Add each processed term to the index with .add_term().

if __name__ == "__main__":
    corpus_path = Path()
    d = DirectoryCorpus.load_text_directory(corpus_path, ".txt")

    # Build the index over this directory.
    index = index_corpus(d)
    
    # We aren't ready to use a full query parser;
    # for now, we'll only support single-term queries.
    query = "whale" # hard-coded search for "whale"
    for p in index.get_postings(query):
        print(f"Document ID {p.doc_id}")

    # TODO: fix this application so the user is asked for a term to search.
