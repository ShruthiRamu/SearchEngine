from indexes import Posting


def merge(x: [Posting], y: [Posting], op: str):
  """
  Do pairwise merge of posting x and y based on the logical operator, op.
  Assume x & y sorted.
  """
  i = 0 # Index of x
  j = 0 # Index of y
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
      if x[i].doc_id != y[j].doc_id:
        merged_posting.append(x[i])
      i += 1
      j += 1
    while i < len(x):
      merged_posting.append(x[i])
      i += 1

  return merged_posting

def merge_phraseliterals(x: [Posting], y: [Posting], difference) :
  """
    Do pairwise positional merge of posting x and y based on the phrase literal logic
    Assume x & y sorted.
    """
  #  TODO: Yet to fix this function to work as expected.
  i = 0  # Index of x
  j = 0  # Index of y

  k = 0  # Index of positions of x
  l = 0  # Index of positions of y
  merged_posting = []

  while i<len(x) and j<len(y):
    if x[i].doc_id == y[j].doc_id :
      positions_x = x[i].positions
      positions_y = y[j].positions
      k=0
      l=0
      while k<len(positions_x) and l<len(positions_y):
        if positions_y[l] - positions_x[k] == difference:
          # add the first document id
          if len(merged_posting) == 0:
            merged_posting.append(x[i])
          # do not add duplicate
          if len(merged_posting) !=0 and x[i].doc_id != merged_posting[-1].doc_id:
            merged_posting.append(x[i])
        k+=1
        l+=1

    i += 1
    j += 1

  return merged_posting
