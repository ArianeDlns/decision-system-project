import numpy as np 
import pandas as pd
import sys
sys.path.append('./')

from generator import GradesGenerator
from modelSAT_test_mag import SAT_Solver


if __name__ == '__main__':
    size = 100
    nb_grades = 5
    noise = 0

    gen = GradesGenerator(size=size, nb_grades=nb_grades,noise=noise)
    grades,admission = gen.generate_grades()
    gen.analyze_gen()


    #Gurobi
    #MRSort_solv = MRSort_Solver(gen)
    #MRSort_solv.set_constraint('MaxMin')
    #MRSort_solv.solve()
    #f1_score_, accuracy_, time_, error_count = MRSort_solv.get_results()

    #SAT
    SAT_solv = SAT_Solver(gen)
    SAT_solv.init_clauses()
    SAT_solv.solve()
    #f1_score_, accuracy_, time_, error_count = SAT_solv.get_results()