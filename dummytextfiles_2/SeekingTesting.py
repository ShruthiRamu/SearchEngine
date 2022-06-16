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

start_byte_position = b_tree["cat"]
num_bytes = 4
postings = []
with open(posting_path, "rb") as f:
    f.seek(start_byte_position)
    #print(f"Before Position: {pos}")
    dft = unpack(">i", f.read(num_bytes))[0]
    pos = start_byte_position + num_bytes
    #print(f"After Position: {pos}")

    prev_doc_id = 0
    for _ in range(dft):
        doc_id = unpack(">i", f.read(num_bytes))[0]
        pos += num_bytes

        doc_id += prev_doc_id # Ungapping DocID
        prev_doc_id = doc_id

        tftd = unpack(">i", f.read(num_bytes))[0]
        pos += num_bytes

        print(f"Term Frequency: {tftd}, Position: {pos}")
        posting = Posting(doc_id=doc_id, tftd=tftd)
        postings.append(posting)
        pos += (tftd * num_bytes)
        f.seek(pos)
        #print("Current File Position: ", f.tell()())

for post in postings:
    print(post)
