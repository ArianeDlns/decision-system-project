from itertools import chain
from itertools import combinations
import csv 

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

def read_data_csv(path: str="data", data: str='/data6crit50ex.csv'):
    with open(path+data, 'r') as file:
        data = list(csv.reader(file))
        data = [row[0].split(";") for row in data]

        size = int(data[2][2])
        nb_grades = int(data[2][0])
        nb_class = int(data[2][1])-1

        grades = [[int(data[i][j+1]) for j in range(nb_grades)] for i in range(3, 3+size)]
        admission = [(int(data[i][nb_grades+1]) - 1) for i in range(3, 3+size)]    
    return grades,admission, size, nb_grades, nb_class