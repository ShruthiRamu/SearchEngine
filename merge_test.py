class Posting:
    """A Posting encapulates a document ID associated with a search query component."""
    def __init__(self, doc_id : int, position=-1):
        self.doc_id = doc_id
        self.positions = [] if position == -1 else position

    def __str__(self):
        if self.positions:
            return f"(ID: {self.doc_id }, -> {[pos for pos in self.positions]})"
        return str(self.doc_id)

def merge_phrase(x, y, offset):
    p_list = []  # A list of resulting posting
    i = 0
    j = 0
    while i < len(x) and j < len(y):
        if x[i].doc_id == y[j].doc_id:
            posting = Posting(x[i].doc_id)
            post1_idx = 0
            post2_idx = 0
            while post1_idx < len(x[i].positions) and post2_idx < len(y[j].positions):
                if abs(y[j].positions[post2_idx] - x[i].positions[post1_idx]) <= offset:
                    if abs(y[j].positions[post2_idx] - x[i].positions[post1_idx]) == offset:
                        posting.positions.append(x[i].positions[post1_idx])
                    post2_idx += 1
                else:
                    post1_idx += 1

            while post1_idx < len(x[i].positions):
                if abs(y[j].positions[-1] - x[i].positions[post1_idx]) == offset:
                    posting.positions.append(x[i].positions[post1_idx])
                post1_idx += 1
            while post2_idx < len(y[j].positions):
                if abs(y[j].positions[post2_idx] - x[i].positions[-1]) == offset:
                    posting.positions.append(x[i].positions[-1])
                post2_idx += 1

            if posting.positions:
                p_list.append(posting)

            i += 1
            j += 1

        elif x[i].doc_id < y[j].doc_id:
            i += 1
        else:
            j += 1

    return p_list


dictionary = {
    "angels": [
        Posting(2, [36, 174, 252, 651]), Posting(4, [12, 22, 102, 432]), Posting(7, [17])
    ],
    "dog": [
        Posting(2, [651, 999]),
    ],
    "god": [
        Posting(2, [4, 170, 652]), Posting(5, [9]), Posting(7, [18])
    ],

    "buffoon": [
        Posting(2, [653, 999]), Posting(5, [10])
    ],
    "fools": [
        Posting(2, [1, 17, 74, 222]), Posting(4, [8, 78, 108, 458]), Posting(7, [3, 13, 23, 193])
    ],
    "fear": [
        Posting(2, [87, 704, 722, 901]), Posting(4, [13, 43, 113, 433]), Posting(7, [18, 328, 528])
    ],
    "in": [
        Posting(2, [3, 37, 76, 444, 851]), Posting(4, [10, 20, 110, 470, 500]), Posting(7, [5, 15, 25, 195])
    ],
    "rush": [
        Posting(2, [2, 66, 194, 321, 702]), Posting(4, [9, 69, 149, 429, 569]), Posting(7, [4, 14, 104])
    ],
    "to": [
        Posting(2, [47, 86, 234, 999]), Posting(4, [14, 24, 774, 944]), Posting(7, [199, 319, 599, 709])
    ],
    "tread": [
        Posting(2, [57, 94, 333]), Posting(4, [15, 35, 155]), Posting(7, [20, 320])
    ],
}

query = 'dog god'
component = query.split(" ")
posting1 = dictionary[component[0]]
for i, comp in enumerate(component[1:]):
  posting2 = dictionary[comp]
  print('dog:')
  for p in posting1:
    print(p)
  print('god:')
  for p in posting2:
    print(p)
  posting1 = merge_phrase(posting1, posting2, i+1)

doc_ids = [p.doc_id for p in posting1]
print(f"Query: {query}, Doc IDs:{doc_ids}")
print('*'*80)



#
# query = 'fools rush in'
# component = query.split(" ")
# posting1 = dictionary[component[0]]
# for i, comp in enumerate(component[1:]):
#   posting2 = dictionary[comp]
#   posting1 = merge_phrase(posting1, posting2, i+1)
#
# doc_ids = [p.doc_id for p in posting1]
# print(f"Query: {query}, Doc IDs:{doc_ids}")
# print('*'*80)
#
# query = 'angels fear to tread'
# component = query.split(" ")
# posting1 = dictionary[component[0]]
# for i, comp in enumerate(component[1:]):
#   posting2 = dictionary[comp]
#   posting1 = merge_phrase(posting1, posting2, i+1)
#
# doc_ids = [p.doc_id for p in posting1]
# print(f"Query: {query}, Doc IDs:{doc_ids}")
# print('*'*80)
#
# query = 'angels god'
# component = query.split(" ")
# posting1 = dictionary[component[0]]
# for i, comp in enumerate(component[1:]):
#   posting2 = dictionary[comp]
#   posting1 = merge_phrase(posting1, posting2, i+1)
#
# doc_ids = [p.doc_id for p in posting1]
# print(f"Query: {query}, Doc IDs:{doc_ids}")
# print('*'*80)
#
# query = 'angels god buffoon'
# component = query.split(" ")
# posting1 = dictionary[component[0]]
# for i, comp in enumerate(component[1:]):
#   posting2 = dictionary[comp]
#   posting1 = merge_phrase(posting1, posting2, i+1)
#
# doc_ids = [p.doc_id for p in posting1]
# print(f"Query: {query}, Doc IDs:{doc_ids}")
# print("*"*80)










