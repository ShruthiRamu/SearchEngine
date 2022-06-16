from typing import List
from . import Posting, Index
from diskindexwriter import DiskIndexWriter
from struct import unpack


class DiskPositionalIndex(Index):

    def __init__(self, disk_index_writer: DiskIndexWriter):
        self.disk_index_writer = disk_index_writer

    def get_positional_postings(self, term: str) -> List[Posting]:
        # Start byte location of term in postings.bin
        # start_byte_position = self.disk_index_writer.b_tree[term]
        start_byte_position = self.disk_index_writer.get_byte_position(term)
        # Read from on-disk postings.bin index
        num_bytes = 4
        postings = []
        with open(self.disk_index_writer.posting_path, "rb") as f:
            f.seek(start_byte_position)
            dft = unpack(">i", f.read(num_bytes))[0]

            prev_doc_id = 0
            for _ in range(dft):
                doc_id = unpack(">i", f.read(num_bytes))[0]
                doc_id += prev_doc_id  # Ungapping DocID
                prev_doc_id = doc_id
                posting = Posting(doc_id=doc_id)

                tftd = unpack(">i", f.read(num_bytes))[0]
                prev_pos = 0
                for _ in range(tftd):
                    position = unpack(">i", f.read(num_bytes))[0]
                    position += prev_pos  # Ungapping position
                    prev_pos = position
                    posting.positions.append(position)

                postings.append(posting)
        return postings

    def get_postings(self, term: str) -> List[Posting]:
        # Start byte location of term in postings.bin
        #start_byte_position = self.disk_index_writer.b_tree[term]
        start_byte_position = self.disk_index_writer.get_byte_position(term)
        # Read from on-disk postings.bin index
        num_bytes = 4
        postings = []
        print(f"Start Byte Position Read: ", start_byte_position)
        with open(self.disk_index_writer.posting_path, "rb") as f:
            f.seek(start_byte_position)
            dft = unpack(">i", f.read(num_bytes))[0]
            pos = start_byte_position + num_bytes

            prev_doc_id = 0
            for _ in range(dft):
                doc_id = unpack(">i", f.read(num_bytes))[0]
                pos += num_bytes

                doc_id += prev_doc_id  # Ungapping DocID
                prev_doc_id = doc_id

                tftd = unpack(">i", f.read(num_bytes))[0]
                pos += num_bytes

                posting = Posting(doc_id=doc_id, tftd=tftd)
                postings.append(posting)

                # Skip positions byte
                pos += (tftd * num_bytes)
                f.seek(pos)

        return postings

    def vocabulary(self) -> List[str]:
        """A (sorted) list of all terms in the index vocabulary."""
        vocab = list(self.disk_index_writer.b_tree.keys())
        vocab.sort()
        return vocab

    def get_doc_weight(self, doc_id:int, filename="docWeights.bin") -> float:
        num_bytes = 8
        start_byte_position = doc_id * num_bytes
        with open(filename, "rb") as f:
            f.seek(start_byte_position)
            Ld = unpack(">d", f.read(num_bytes))[0]
        return Ld
