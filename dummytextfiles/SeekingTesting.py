from pathlib import Path
from indexes.postings import Posting
from struct import unpack
posting_path = Path("index/postings.bin")

b_tree = {'among': 0, 'best': 16, 'california': 44, 'debt': 60, 'in': 76, 'increas': 128, 'is': 144, 'lab': 160, 'new': 176, 'not': 244, 'open': 260, 'rank': 276, 'scienc': 304, 'state': 320, 'student': 348, 'univers': 364, 'york': 428}

term = 'york'
start_byte_position = b_tree[term]
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

print("Posting for ", term)
for post in postings:
    print(post)