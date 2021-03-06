import numpy as np 
import pandas as pd
import sys
sys.path.append('./')

from generator import GradesGenerator
from models import MRSort_Solver, SAT_Solver, Max_SAT_Solver

from utils.argument import parse_arguments
from utils.helpers import read_data_csv

if __name__ == '__main__':
    args = parse_arguments()
    size = args.size
    nb_grades = args.nb_grades
    noise = args.noise
    nb_class = args.nb_class
    model = args.model
    seed = args.seed
    csv = args.csv

    if csv == '':
        gen = GradesGenerator(size=size, nb_grades=nb_grades,noise=noise,seed=seed, nb_class=nb_class)
        grades,admission = gen.generate_grades()
        gen.analyze_gen()
    else:
        grades, admission, size, nb_grades, nb_class = read_data_csv(data=args.csv)
        gen = GradesGenerator(size=size, nb_grades=nb_grades,noise=noise, seed=seed, nb_class=nb_class)
        gen.analyze_gen(admission)

    if model == 'MILP':
        MRSort_solv = MRSort_Solver(gen)
        if csv != '':
            MRSort_solv = MRSort_Solver(gen,grades=grades, admission=admission)
        MRSort_solv.set_constraint('MaxMin')
        MRSort_solv.solve()
        f1_score_, accuracy_, time_, error_count = MRSort_solv.get_results()
    elif model == 'SAT': 
        grades,admissions = gen.generate_grades()
        SAT_Solv = SAT_Solver(generator=gen)
        SAT_Solv.init_clauses(grades,admissions)
        f1_score_, accuracy_, time_, error_rate = SAT_Solv.get_results(grades,admissions)
    elif model == 'Max-SAT': 
        grades,admissions = gen.generate_grades()
        Max_SAT_Solv = Max_SAT_Solver(generator=gen)
        Max_SAT_Solv.init_clauses(grades,admissions)
        f1_score_, accuracy_, time_, error_rate = Max_SAT_Solv.get_results(grades,admissions)
    else:
        print("Please choose model between ['']")