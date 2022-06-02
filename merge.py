def merge(x, y, op):
    """
  Do pairwise merge of posting x and y based on the logical operator, op.
  Assume x & y sorted.
  """
    i = 0  # Index of x
    j = 0  # Index of j
    merged_posting = []

    if op == 'and':
        while i < len(x) and j < len(y):
            if x[i] == y[j]:
                merged_posting.append(x[i])
                i += 1
                j += 1
            elif x[i] > y[j]:
                j += 1
            elif x[i] < y[j]:
                i += 1

    elif op == 'or':
        while i < len(x) and j < len(y):
            if x[i] == y[j]:
                merged_posting.append(x[i])
                i += 1
                j += 1
            elif x[i] > y[j]:
                # Smaller doc id goes into list first
                merged_posting.append(y[j])
                j += 1
            elif x[i] < y[j]:
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
            if x[i] != y[j]:
                merged_posting.append(x[i])
            i += 1
            j += 1
        while i < len(x):
            merged_posting.append(x[i])
            i += 1

    return merged_posting


A = [1, 4, 7, 8, 10, 13, 20, 24, 25, 26, 29, 41, 53, 55]
B = [1, 5, 9, 11, 12, 13, 18, 24, 25, 28, 29, 40, 52]
print(merge(A, B, 'and'))
print(merge(A, B, 'or'))
print(merge(A, B, 'and not'))