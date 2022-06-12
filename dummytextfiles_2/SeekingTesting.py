from pathlib import Path
from indexes.postings import Posting
from struct import unpack
posting_path = Path("index/postings.bin")

b_tree = {
    'cat': 0,
    'dog': 32,
    'fast': 48,
    'high': 64,
    'jump': 80,
    'run': 96
}

start_byte_position = b_tree["fast"]
num_bytes = 4
postings = []
with open(posting_path, "rb") as f:
    f.seek(start_byte_position)
    dft = unpack(">i", f.read(num_bytes))[0]
    prev_doc_id = 0
    for _ in range(dft):
        doc_id = unpack(">i", f.read(num_bytes))[0]

        doc_id += prev_doc_id # Ungapping DocID
        prev_doc_id = doc_id
        posting = Posting(doc_id=doc_id)

        tftd = unpack(">i", f.read(num_bytes))[0]

        prev_pos = 0
        for _ in range(tftd):
            position = unpack(">i", f.read(num_bytes))[0]

            position += prev_pos # Ungapping position
            prev_pos = position
            posting.positions.append(position)

        postings.append(posting)

for post in postings:
    print(post)
