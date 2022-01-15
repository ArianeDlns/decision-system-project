from itertools import chain
from itertools import combinations

def powerset(iterable): 
            s = list(iterable)
            return( chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))

def get_i2v(v2i_alpha, v2i_beta,A):
    i2v = {}

    for i in range(len(v2i_alpha)):
        i2v[i+1] = list(v2i_alpha.keys())[list(v2i_alpha.values()).index(i+1)]

    for i in range(len(v2i_beta)):
        i2v[i+A+1] = list(v2i_beta.keys())[list(v2i_beta.values()).index(i+1+A)]
    return i2v