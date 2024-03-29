from typing import List
from . import Posting, Index
from diskindexwriter import DiskIndexWriter
from struct import unpack


def VBDecode(bytestream):
    number = 0
    n = 0
    for i in range(len(bytestream)):
        if bytestream[i] < 128:
            n = 128 * n + bytestream[i]
        else:
            n = 128 * n + (bytestream[i] - 128)
            number += n
            n = 0
    return number


class DiskPositionalIndex(Index):

    def __init__(self, disk_index_writer: DiskIndexWriter, num_docs=0):
        self.disk_index_writer = disk_index_writer
        self.num_docs = num_docs
        self.f = open(self.disk_index_writer.posting_path, "rb")

    def get_positional_postings(self, term: str) -> List[Posting]:
        # Start byte location of term in postings.bin
        # start_byte_position = self.disk_index_writer.b_tree[term]
        start_byte_position = self.disk_index_writer.get_byte_position(term)
        postings = []
        if start_byte_position != -1:
            # Read from on-disk postings.bin index
            num_bytes = 1
            #with open(self.disk_index_writer.posting_path, "rb") as f:
            self.f.seek(start_byte_position)
            dft = ord(self.f.read(num_bytes))
            dft_arr = []

            # append all bits belonging to same number to array
            while True:
                if dft < 128:
                    dft_arr.append(dft)
                    dft = ord(self.f.read(num_bytes))
                else:
                    dft_arr.append(dft)
                    break
            dft = VBDecode(dft_arr)

            prev_doc_id = 0
            for _ in range(dft):
                doc_id = ord(self.f.read(num_bytes))

                doc_id_arr = []
                while True:
                    if doc_id < 128:
                        doc_id_arr.append(doc_id)
                        doc_id = ord(self.f.read(num_bytes))
                    else:
                        doc_id_arr.append(doc_id)
                        break
                doc_id = VBDecode(doc_id_arr)

                doc_id += prev_doc_id  # Ungapping DocID
                prev_doc_id = doc_id
                posting = Posting(doc_id=doc_id)

                tftd = ord(self.f.read(num_bytes))
                tftd_arr = []
                while True:
                    if tftd < 128:
                        tftd_arr.append(tftd)
                        tftd = ord(self.f.read(num_bytes))
                    else:
                        tftd_arr.append(tftd)
                        break
                tftd = VBDecode(tftd_arr)
                prev_pos = 0
                for _ in range(tftd):
                    position = ord(self.f.read(num_bytes))
                    pos_arr = []
                    while True:
                        if position < 128:
                            pos_arr.append(position)
                            position = ord(self.f.read(num_bytes))
                        else:
                            pos_arr.append(position)
                            break
                    position = VBDecode(pos_arr)
                    position += prev_pos  # Ungapping position
                    prev_pos = position
                    posting.positions.append(position)
                postings.append(posting)

        return postings

    def get_postings(self, term: str) -> List[Posting]:
        # Start byte location of term in postings.bin
        # start_byte_position = self.disk_index_writer.b_tree[term]
        start_byte_position = self.disk_index_writer.get_byte_position(term)
        postings = []
        # print(f"Start Byte Position Read: ", start_byte_position)
        num_bytes = 1
        with open(self.disk_index_writer.posting_path, "rb") as f:
            # Handling missing terms to avoid errors, for precision and recall change
            if start_byte_position != -1:
                f.seek(start_byte_position)
            # dft = unpack(">i", f.read(num_bytes))[0]
            dft = ord(f.read(num_bytes))
            dft_arr = []

            # append all bits belonging to same number to array
            while True:
                if dft < 128:
                    dft_arr.append(dft)
                    dft = ord(f.read(num_bytes))
                else:
                    dft_arr.append(dft)
                    break
            dft = VBDecode(dft_arr)
            # pos = start_byte_position + num_bytes

            prev_doc_id = 0
            for _ in range(dft):
                doc_id = ord(f.read(num_bytes))
                # pos += num_bytes
                doc_id_arr = []

        if start_byte_position != -1:
            # Read from on-disk postings.bin index
            num_bytes = 1

            # print(f"Start Byte Position Read: ", start_byte_position)
            with open(self.disk_index_writer.posting_path, "rb") as f:
                f.seek(start_byte_position)
                # dft = unpack(">i", f.read(num_bytes))[0]
                dft = ord(f.read(num_bytes))
                dft_arr = []

                # append all bits belonging to same number to array
                while True:
                    if dft < 128:
                        dft_arr.append(dft)
                        dft = ord(f.read(num_bytes))
                    else:
                        dft_arr.append(dft)
                        break
                dft = VBDecode(dft_arr)
                # pos = start_byte_position + num_bytes

                prev_doc_id = 0
                for _ in range(dft):
                    doc_id = ord(f.read(num_bytes))
                    # pos += num_bytes
                    doc_id_arr = []
                    while True:
                        if doc_id < 128:
                            doc_id_arr.append(doc_id)
                            doc_id = ord(f.read(num_bytes))
                        else:
                            doc_id_arr.append(doc_id)
                            break
                    doc_id = VBDecode(doc_id_arr)

                    doc_id += prev_doc_id  # Ungapping DocID
                    prev_doc_id = doc_id

                    tftd = ord(f.read(num_bytes))
                    tftd_arr = []
                    while True:
                        if tftd < 128:
                            tftd_arr.append(tftd)
                            tftd = ord(f.read(num_bytes))
                        else:
                            tftd_arr.append(tftd)
                            break
                    tftd = VBDecode(tftd_arr)
                    pos_count = 0
                    # pos += num_bytes
                    # Scan past position bytes
                    while pos_count < tftd:
                        position = ord(f.read(num_bytes))
                        if position < 128:
                            continue
                        else:
                            pos_count += 1

                    posting = Posting(doc_id=doc_id, tftd=tftd)
                    postings.append(posting)

                    # Skip positions byte
                    # pos += (tftd * num_bytes)
                    # f.seek(pos)
        #print("Returning postings: ", postings)
        return postings

    def vocabulary(self) -> List[str]:
        """A (sorted) list of all terms in the index vocabulary."""
        vocab = []
        with open(self.disk_index_writer.vocab_list_path, "r") as f:
            for term in f:
                vocab.append(term.strip())
        return vocab

    def get_doc_info(self, doc_id: int, doc_info: str) -> float:
        doc_info_dict = {"Ld": 0, "docLength": 1, "byte_size": 2, "avg_tftd": 3}
        num_bytes = 8
        start_byte_position = doc_id * 32 + (doc_info_dict[doc_info] * num_bytes)
        # print("start_byte_position: ", start_byte_position)
        with open(self.disk_index_writer.doc_weights_path, "rb") as f:
            f.seek(start_byte_position)
            doc_param = unpack(">d", f.read(num_bytes))[0]
        return doc_param

    def get_avg_tokens_corpus(self) -> float:
        with open(self.disk_index_writer.avg_tokens_path, 'rb') as f:
            avg_tokens_length = unpack(">d", f.read(8))[0]
        return avg_tokens_length
