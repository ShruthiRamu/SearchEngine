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
