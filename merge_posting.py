from indexes import Posting


def merge(x: [Posting], y: [Posting], op: str):
    """
  Do pairwise merge of posting x and y based on the logical operator, op.
  Assume x & y sorted.
  """
    i = 0  # Index of x
    j = 0  # Index of y
    merged_posting = []

    if op == 'and':
        while i < len(x) and j < len(y):
            if x[i].doc_id == y[j].doc_id:
                merged_posting.append(x[i])
                i += 1
                j += 1
            elif x[i].doc_id > y[j].doc_id:
                j += 1
            elif x[i].doc_id < y[j].doc_id:
                i += 1

    elif op == 'or':
        while i < len(x) and j < len(y):
            if x[i].doc_id == y[j].doc_id:
                merged_posting.append(x[i])
                i += 1
                j += 1
            elif x[i].doc_id > y[j].doc_id:
                # Smaller doc id goes into list first
                merged_posting.append(y[j])
                j += 1
            elif x[i].doc_id < y[j].doc_id:
                merged_posting.append(x[i])
                i += 1
        # Place leftover into posting list
        while i < len(x):
            merged_posting.append(x[i])
            i += 1
        while j < len(y):
            merged_posting.append(y[j])
            j += 1

    elif op == 'and not':
        while i < len(x) and j < len(y):
            if x[i].doc_id == y[j].doc_id:
                i += 1
                j += 1
            elif x[i].doc_id < y[j].doc_id:
                merged_posting.append(x[i])
                i += 1
            elif y[j].doc_id < x[i].doc_id:
                j += 1
        while i < len(x):
            merged_posting.append(x[i])
            i += 1

    return merged_posting


def merge_phrase(posting1: [Posting], posting2: [Posting], offset):
    """
    Do pairwise positional merge of posting positions of x and y based on the phrase literal logic
    Assume x & y sorted.
    """
    p_list = []  # A list of resulting posting
    i = 0  # Posting 1 index
    j = 0  # Posting 2 index

    while i < len(posting1) and j < len(posting2):
        if posting1[i].doc_id == posting2[j].doc_id:
            posting = Posting(posting1[i].doc_id)
            pos1_idx = 0  # Posting 1's position index
            pos2_idx = 0  # Posting 2's position index
            while pos1_idx < len(posting1[i].positions) and pos2_idx < len(posting2[j].positions):
                if posting2[j].positions[pos2_idx] - posting1[i].positions[pos1_idx] != offset:
                    # Move smaller pointer
                    # [65,99]
                    # [1,2,66]
                    if posting1[i].positions[pos1_idx] < posting2[j].positions[pos2_idx]:
                        pos1_idx += 1
                    elif posting2[j].positions[pos2_idx] < posting1[i].positions[pos1_idx]:
                        pos2_idx += 1
                    # if they are equal
                    else:
                        pos1_idx += 1
                        pos2_idx += 1
                else:
                    posting.positions.append(posting1[i].positions[pos1_idx])
                    pos1_idx += 1
                    pos2_idx += 1

            while pos1_idx < len(posting1[i].positions):
                if posting2[j].positions[-1] - posting1[i].positions[pos1_idx] == offset:
                    posting.positions.append(posting1[i].positions[pos1_idx])
                pos1_idx += 1
            while pos2_idx < len(posting2[j].positions):
                if posting2[j].positions[pos2_idx] - posting1[i].positions[-1] == offset:
                    posting.positions.append(posting1[i].positions[-1])
                pos2_idx += 1

            if posting.positions:
                p_list.append(posting)

            i += 1
            j += 1

        elif posting1[i].doc_id < posting2[j].doc_id:
            i += 1
        else:
            j += 1
    return p_list


def merge_phrase_textbook(x, y, offset):
    answer = []  # A list of resulting posting
    i = 0
    j = 0
    while i < len(x) and j < len(y):
        if x[i].doc_id == y[j].doc_id:
            l = []
            posting = Posting(x[i].doc_id)
            post1_idx = 0
            post2_idx = 0
            pp1 = x[i].positions  # positions of x
            pp2 = y[j].positions  # positions of y
            while post1_idx < len(x[i].positions):
                while post2_idx < len(y[j].positions):
                    if abs(pp1[post1_idx] - pp2[post2_idx]) <= offset:
                        l.append(pp2[post2_idx])
                    elif pp2[post2_idx] > pp1[post1_idx]:
                        break
                    post2_idx += 1
                while l != [] and abs(l[0] - pp1[post1_idx]) > offset:
                    l.remove(l[0])
                for ps in l:
                    posting.positions.append(pp1[post1_idx])
                    posting.positions.append(ps)
                    answer.append(posting)
                post1_idx += 1
            i += 1
            j += 1

        elif x[i].doc_id < y[j].doc_id:
            i += 1
        else:
            j += 1

    return answer


# def merge_phrase(x: [Posting], y: [Posting], offset):
#     p_list = []  # A list of resulting posting
#     i = 0
#     j = 0
#     while i < len(x) and j < len(y):
#         if x[i].doc_id == y[j].doc_id:
#             posting = Posting(x[i].doc_id)
#             post1_idx = 0
#             post2_idx = 0
#             while post1_idx < len(x[i].positions) and post2_idx < len(y[j].positions):
#                 if abs(y[j].positions[post2_idx] - x[i].positions[post1_idx]) <= offset:
#                     if abs(y[j].positions[post2_idx] - x[i].positions[post1_idx]) == offset:
#                         posting.positions.append(x[i].positions[post1_idx])
#                     post2_idx += 1
#                 else:
#                     post1_idx += 1
#
#             while post1_idx < len(x[i].positions):
#                 if abs(y[j].positions[-1] - x[i].positions[post1_idx]) == offset:
#                     posting.positions.append(x[i].positions[post1_idx])
#                 post1_idx += 1
#             while post2_idx < len(y[j].positions):
#                 if abs(y[j].positions[post2_idx] - x[i].positions[-1]) == offset:
#                     posting.positions.append(x[i].positions[-1])
#                 post2_idx += 1
#
#             if posting.positions:
#                 p_list.append(posting)
#
#             i += 1
#             j += 1
#
#         elif x[i].doc_id < y[j].doc_id:
#             i += 1
#         else:
#             j += 1
#
#     print("Merge phrase: ", p_list)
#     return p_list


def merge_phraseliterals(x: [Posting], y: [Posting], difference):
    """
    Do pairwise positional merge of posting positions of x and y based on the phrase literal logic
    Assume x & y sorted.
    """
    i = 0  # Index of x
    j = 0  # Index of y

    # k = 0  # Index of positions of x
    # l = 0  # Index of positions of y
    merged_posting = []

    while i < len(x) and j < len(y):
        # check if the term is present in both the document
        if x[i].doc_id == y[j].doc_id:
            # get the positions list for the document
            positions_x = x[i].positions  # Index of positions of x
            positions_y = y[j].positions  # Index of positions of y
            k = 0
            l = 0

            while k < len(positions_x) and l < len(positions_y):
                # check if the difference of the positions is what we are looking for
                # TODO: Update this to just check if the difference is 1 or off by 1, may be no need to have this parameter
                if positions_y[l] - positions_x[k] == difference:
                    # if they are adjacent add them to our merged result
                    # add the first ever document id to the list
                    if len(merged_posting) == 0:
                        merged_posting.append(x[i])
                    # do not add duplicate from the next iteration
                    if len(merged_posting) != 0 and y[j].doc_id != merged_posting[-1].doc_id:
                        merged_posting.append(x[i])
                    # Do we need to check the next positions once we are matched?
                    k += 1
                    l += 1
                    # check if the positions are the same

                    # # add the first ever document id to the list
                    # if len(merged_posting) == 0:
                    #     merged_posting.append(x[i])
                    # # do not add duplicate from the next iteration
                    # if len(merged_posting) != 0 and x[i].doc_id != merged_posting[-1].doc_id:
                    #     merged_posting.append(x[i])
                    # k += 1
                    l += 1
                elif positions_y[l] < positions_x[k]:
                    l += 1
                # Check with professor what to do if the lower term position is > higher term position
                elif positions_y[l] > positions_x[k]:
                    l += 1
                # check how to handle this and when to increment the k
                else:
                    k += 1
            i += 1
            j += 1

        # if the first list contains later documents handle it
        elif x[i].doc_id > y[j].doc_id:
            j += 1
        # If the second list contains later document handle it
        elif y[j].doc_id > x[i].doc_id:
            i += 1

    return merged_posting


def near_k_merge(posting1: [Posting], posting2: [Posting], k):
    merged_postings = []
    i = 0  # index for posting 1
    j = 0  # index for posting 2

    while i < len(posting1) and j < len(posting2):
        if posting1[i].doc_id == posting2[j].doc_id:
            posting = Posting(posting1[i].doc_id)
            pos1_idx = 0  # Posting 1's position index
            pos2_idx = 0  # Posting 2's position index
            while pos1_idx < len(posting1[i].positions) and pos2_idx < len(posting2[j].positions):
                if posting2[j].positions[pos2_idx] - posting1[i].positions[pos1_idx] != k:
                    # Move smaller pointer
                    if posting1[i].positions[pos1_idx] < posting2[j].positions[pos2_idx]:
                        pos1_idx += 1
                    elif posting2[j].positions[pos2_idx] < posting1[i].positions[pos1_idx]:
                        pos2_idx += 1
                    # if they are equal
                    else:
                        pos1_idx += 1
                        pos2_idx += 1
                else:
                    #posting.positions.append(posting1[i].positions[pos1_idx])  # <=k
                    posting.positions.append(posting2[j].positions[pos2_idx])
                    pos1_idx += 1
                    pos2_idx += 1

            while pos1_idx < len(posting1[i].positions) and pos2_idx < len(posting2[j].positions):
                if posting2[j].positions[-1] - posting1[i].positions[pos1_idx] <= k:
                    #posting.positions.append(posting1[i].positions[pos1_idx])
                    posting.positions.append(posting2[j].positions[pos2_idx])
                pos1_idx += 1
            while pos2_idx < len(posting2[j].positions):
                if posting2[j].positions[pos2_idx] - posting1[i].positions[-1] <= k:
                    #posting.positions.append(posting1[i].positions[-1])
                    posting.positions.append(posting2[j].positions[pos2_idx])
                pos2_idx += 1

            if posting.positions:
                merged_postings.append(posting)

            i += 1
            j += 1

        elif posting1[i].doc_id < posting2[j].doc_id:
            i += 1
        else:
            j += 1
    return merged_postings


def and_merge(x: [Posting], y: [Posting]):
    i = 0  # Index of x
    j = 0  # Index of y
    merged_posting = []
    while i < len(x) and j < len(y):
        if x[i].doc_id == y[j].doc_id:
            merged_posting.append(x[i])
            i += 1
            j += 1
        elif x[i].doc_id > y[j].doc_id:
            j += 1
        elif x[i].doc_id < y[j].doc_id:
            i += 1
    return merged_posting


def or_merge(x: [Posting], y: [Posting]):
    i = 0  # Index of x
    j = 0  # Index of y
    merged_posting = []
    while i < len(x) and j < len(y):
        if x[i].doc_id == y[j].doc_id:
            merged_posting.append(x[i])
            i += 1
            j += 1
        elif x[i].doc_id > y[j].doc_id:
            # Smaller doc id goes into list first
            merged_posting.append(y[j])
            j += 1
        elif x[i].doc_id < y[j].doc_id:
            merged_posting.append(x[i])
            i += 1
        # Place leftover into posting list
    while i < len(x):
        merged_posting.append(x[i])
        i += 1
    while j < len(y):
        merged_posting.append(y[j])
        j += 1
    return merged_posting


def and_not_merge(x: [Posting], y: [Posting]):
    i = 0  # Index of x
    j = 0  # Index of y
    merged_posting = []
    while i < len(x) and j < len(y):
        if x[i].doc_id == y[j].doc_id:
            i += 1
            j += 1
        elif x[i].doc_id < y[j].doc_id:
            merged_posting.append(x[i])
            i += 1
        elif y[j].doc_id < x[i].doc_id:
            j += 1
    while i < len(x):
        merged_posting.append(x[i])
        i += 1
    return merged_posting
