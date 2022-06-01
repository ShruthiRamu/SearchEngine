from string import ascii_lowercase


def get_encoding():
    """ Encodes each letter to a digit """
    ch_encoding = {}
    for char in ascii_lowercase:
        if char in {'b', 'f', 'p', 'v'}:
            ch_encoding[char] = 1
        elif char in {'c', 'g', 'j', 'k', 'q', 's', 'x', 'z'}:
            ch_encoding[char] = 2
        elif char in {'d', 't'}:
            ch_encoding[char] = 3
        elif char in {'l'}:
            ch_encoding[char] = 4
        elif char in {'m', 'n'}:
            ch_encoding[char] = 5
        elif char in {'r'}:
            ch_encoding[char] = 6
        else:
            ch_encoding[char] = 0
    return ch_encoding


def soundex_code(term, encoding, code_len=4):
    """ Generate 4-character soundex code of the name based on encoding """
    # Letter -> digits
    digits = [encoding[char] for char in term[1:]]
    code = []
    # Remove duplicate adjacent digits
    for i in range(len(digits)-1):
        if digits[i] != digits[i+1]:
            code.append(digits[i])
            if i+1 == len(digits)-1:
                code.append(digits[i+1])
    # Remove zeros
    code = [c for c in code if c != 0]
    # Add trailing zeros
    for _ in range(len(code), code_len-1):
        code.append(0)
    # Retain first letter
    code = term[0].upper() + ''.join([str(c) for c in code])
    return code

# a -> 0 , r -> 6, d -> 3, i -> 0, n -> 5, g -> 2
# What about first name like kyaw htet?
#name = 'harding'
#print(name, ": ", soundex_code(name, encoding=get_encoding()))

# name = 'hermann'
# print(name, ": ", soundex_code(name, encoding=get_encoding()))
# name = 'curie'
# print(name, ": ", soundex_code(name, encoding=get_encoding()))
# name = 'oconner'
# print(name, ": ", soundex_code(name, encoding=get_encoding()))
# term = 'piece'
# print(term, ": ", soundex_code(term, encoding=get_encoding()))
# term = 'peace'
# print(term, ": ", soundex_code(term, encoding=get_encoding()))
# term = 'too'
# print(term, ": ", soundex_code(term, encoding=get_encoding()))
# term = 'two'
# print(term, ": ", soundex_code(term, encoding=get_encoding()))