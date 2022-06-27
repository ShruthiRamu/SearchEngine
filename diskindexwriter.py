from pathlib import Path
from struct import pack
from typing import Iterable
from indexes.index import Index
import sqlite3


# VB encode a single integer
def VB_encode_number(n):
    bytes = []
    while True:
        bytes.insert(0, (n % 128))
        if n < 128:
            break
        n = n // 128
    bytes[-1] += 128
    return bytes


class DiskIndexWriter:

    def __init__(self, index_path: Path, document_weights=[], docLengthd=[],
                 byteSized=[], average_tftd=[], document_tokens_length_average=[]):
        self.index_path = index_path
        self.doc_weights_path = index_path / "docWeights.bin"
        self.posting_path = index_path / "postings.bin"
        self.term_byteposition_path = index_path / "term_byteposition.db"
        self.avg_tokens_path = index_path / "avg_tokens_corpus.bin"
        term_byteposition_exists = self.term_byteposition_path.is_file()
        self._conn = sqlite3.connect(self.term_byteposition_path)
        self._cursor = self._conn.cursor()
        self.vocab_list_path = index_path / "vocab_list.txt"
        if not term_byteposition_exists:
            # print("Createing Table")
            self._cursor.execute("""CREATE TABLE termBytePositions (
                         term text, 
                         byte_position integer
                          )""")
        if document_weights and not self.doc_weights_path.is_file():
            self._write_docWeights(document_weights, docLengthd, byteSized, average_tftd)
        if document_tokens_length_average and not self.avg_tokens_path.is_file():
            self._write_avg_tokens_corpus(document_tokens_length_average=document_tokens_length_average)

    def _write_docWeights(self, document_weights, docLengthd, byteSized, average_tftd):
        # Write Ld as an 8-byte double
        with open(self.doc_weights_path, 'wb') as f:
            for dw, dl, bs, atftd in zip(document_weights, docLengthd, byteSized, average_tftd):
                f.write(pack('>d', float(dw)))
                f.write(pack('>d', float(dl)))
                f.write(pack('>d', float(bs)))
                f.write(pack('>d', float(atftd)))

    def _write_avg_tokens_corpus(self, document_tokens_length_average):
        # Write docLength average as an 8 byte double
        with open(self.avg_tokens_path, 'wb') as f:
            f.write(pack('>d', float(document_tokens_length_average)))

    def write_index(self, index: Index):
        print("Writing index to disk...")
        """
        Write a binary-representation of index at the absolute path
        """
        # mode = 'ab' if absolute_path.is_file() else 'wb'
        mode = 'wb'
        # Format for saving: dft, doc_id, tfd, pos1, pos2...
        with open(self.posting_path, mode) as f:
            vocab = index.vocabulary()  # All Terms Sorted
            # term -> [(Doc_id,[pos1,pos2...]), (Doc_id2, [pos1,...])]
            byte_position = 0  # Current byte position
            # Indicates bytes position of where posting begins for a particular term
            # byte_positions = [byte_position]
            for _, term in enumerate(vocab):
                with self._conn:
                    self._cursor.execute("INSERT INTO termBytePositions VALUES (:term, :byte_position)",
                                         {'term': term, 'byte_position': byte_position})
                # Retrieve postings
                postings = index.get_positional_postings(term)
                # Document Frequency as 4-byte integer
                dft = len(postings)  # Document Frequency
                dft_encode = VB_encode_number(dft)
                for n in dft_encode:
                    f.write(n.to_bytes(1, 'big'))
                byte_position += len(dft_encode)
                # print(f"Term: ", term)
                prev_doc_id = 0
                for posting in postings:
                    # print(f"Posting: ", posting)
                    # Doc ID as 4-byte gap
                    doc_id_gap = posting.doc_id - prev_doc_id
                    id_encode = VB_encode_number(doc_id_gap)
                    for n in id_encode:
                        f.write(n.to_bytes(1, 'big'))
                    byte_position += len(id_encode)
                    prev_doc_id = posting.doc_id
                    # Term Frequency as 4-byte integer
                    tfd = len(posting.positions)
                    tfd_encode = VB_encode_number(tfd)
                    for n in tfd_encode:
                        f.write(n.to_bytes(1, 'big'))
                    byte_position += len(tfd_encode)
                    # Positions as 4-byte gap
                    prev_position = 0
                    for position in posting.positions:
                        position_gap = position - prev_position
                        position_encode = VB_encode_number(position_gap)
                        for n in position_encode:
                            f.write(n.to_bytes(1, 'big'))
                        byte_position += len(position_encode)
                        prev_position = position

        with open(self.vocab_list_path, 'w') as f:
            f.writelines('\n'.join(vocab))

        print("Writing index to disk completed")

    def get_byte_position(self, term: str) -> int:
        self._cursor.execute("SELECT byte_position FROM termBytePositions WHERE term=:term",
                             {'term': term})
        byte_pos = self._cursor.fetchone()
        # if not byte_pos:
        #     print(f"Term {term} doesn't exist in termBytePositions")

        return byte_pos[0] if byte_pos else -1
