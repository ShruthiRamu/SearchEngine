from pathlib import Path
from struct import pack


class DiskIndexWriter():
    def write_index(self, index, absolute_path: Path):
        # check if postings.bin exists

        mode = 'ab' if absolute_path.is_file() else 'wb'

        # Open the file in binary write mode

        # dft, doc_id, tfd, pos1, pos2...
        with open(absolute_path, mode) as f:
            # Ask for vocab
            vocab = index.vocabulary() # all the terms

            # term -> <(Doc_id,[pos1,pos2...])(Doc_id2, [])>

            # Final Result List = []
            # For Each Term
            for term in vocab:
                postings = index.get_postings(term)
                print("Term: ", term)
                for p in postings:
                    print(p)
                # Retreive a list of positing
                # Find its length -> dft
                # append final list
                dft = len(postings)
                f.write(pack('>i', dft))
                # Loop over that posting list
                # posting.doc_id ->
                # append final list
                prev_doc_id = 0
                for posting in postings:
                    id_gap = posting.doc_id - prev_doc_id
                    f.write(pack('>i', id_gap))
                    prev_doc_id = posting.doc_id
                    # tfd = len(positions)
                    # append final list
                    tfd = len(posting.positions)
                    f.write(pack('>i', tfd))
                    # list of positions
                    prev_position = 0
                    for position in posting.positions:
                        position_gap = position - prev_position
                        f.write(pack('>i', position_gap))
                        prev_position = position
                    # Write each pos to file
                    # f.write(struct.pack(">i", docid)) -> 4 bytes


