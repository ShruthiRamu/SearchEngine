from pathlib import Path
from struct import pack
from typing import Iterable
from indexes.index import Index
import sqlite3


class DiskIndexWriter:

    def __init__(self, document_weights):
        self._conn = sqlite3.connect("term_byteposition.db")
        self._cursor = self._conn.cursor()
        self._cursor.execute("""CREATE TABLE termBytePositions (
                     term text, 
                     byte_position integer
                      )""")
        self.b_tree = {} #TODO: DELETE LATER
        self.posting_path = Path()
        self._write_docWeights(document_weights)

    def _write_docWeights(self, document_weights):
        # Write Ld as an 8-byte double
        with open("docWeights.bin", 'wb') as f:
            for doc_weight in document_weights:
                f.write(pack('>d', float(doc_weight)))

    def write_index(self, index: Index, absolute_path: Path) -> Iterable[int]:
        """
        Write a binary-representation of index at the absolute path
        """
        self.posting_path = absolute_path
        #mode = 'ab' if absolute_path.is_file() else 'wb'
        mode = 'wb'
        # Format for saving: dft, doc_id, tfd, pos1, pos2...
        with open(absolute_path, mode) as f:
            vocab = index.vocabulary() # All Terms Sorted
            # term -> [(Doc_id,[pos1,pos2...]), (Doc_id2, [pos1,...])]
            byte_position = 0 # Current byte position
            # Indicates bytes position of where posting begins for a particular term
            #byte_positions = [byte_position]
            for _, term in enumerate(vocab):
                # TODO: REMOVE THE DICTIONARY AFTER TESTING
                self.b_tree[term] = byte_position
                with self._conn:
                    self._cursor.execute("INSERT INTO termBytePositions VALUES (:term, :byte_position)",
                              {'term': term, 'byte_position': byte_position})
                # Retrieve postings
                postings = index.get_positional_postings(term)
                # Document Frequency as 4-byte integer
                dft = len(postings) # Document Frequency
                f.write(pack('>i', dft))
                byte_position += 4
                print(f"Term: ", term)
                prev_doc_id = 0
                for posting in postings:
                    print(f"Posting: ", posting)
                    # Doc ID as 4-byte gap
                    doc_id_gap = posting.doc_id - prev_doc_id
                    f.write(pack('>i', doc_id_gap))
                    byte_position += 4
                    prev_doc_id = posting.doc_id
                    # Term Frequency as 4-byte integer
                    tfd = len(posting.positions)
                    f.write(pack('>i', tfd))
                    byte_position += 4
                    # Positions as 4-byte gap
                    prev_position = 0
                    for position in posting.positions:
                        position_gap = position - prev_position
                        f.write(pack('>i', position_gap))
                        byte_position += 4
                        prev_position = position

    def get_byte_position(self, term: str) -> int:
        self._cursor.execute("SELECT byte_position FROM termBytePositions WHERE term=:term",
                  {'term': term})
        byte_pos = self._cursor.fetchone()
        return byte_pos[0] if byte_pos else -1