from BTrees.OIBTree import OIBTree

b_tree = OIBTree()
b_tree.update({"cat": 1, "dog": 2, "cute": 4})

print("\nSize of B+: ", len(b_tree))