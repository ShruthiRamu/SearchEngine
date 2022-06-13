from pathlib import Path
from struct import pack
from typing import Iterable
from indexes.index import Index
import BTrees


class DiskIndexWriter():

    def __init__(self):
        self.b_tree = {} #TODO: Make it B+ Tree
        self.posting_path = Path()

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
            vocab_size = len(vocab)
            # term -> [(Doc_id,[pos1,pos2...]), (Doc_id2, [pos1,...])]
            byte_position = 0 # Current byte position
            # Indicates bytes position of where posting begins for a particular term
            #byte_positions = [byte_position]

            for _, term in enumerate(vocab):
                self.b_tree[term] = byte_position
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