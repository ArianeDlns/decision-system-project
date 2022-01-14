from itertools import chain
from itertools import combinations

def powerset(iterable): 
    s = list(iterable)
    return(chain.from_iterable(combinations(s, r) for r in range(len(s)+1)))