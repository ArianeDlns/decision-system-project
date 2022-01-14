import numpy as np 
import pandas as pd
import sys
sys.path.append('./')

from generator import GradesGenerator
from models import MRSort_Solver

from utils.argument import parse_arguments

if __name__ == '__main__':
    args = parse_arguments()
    size = args.size
    nb_grades = args.nb_grades
    noise = args.noise
    nb_class = args.nb_class
    model = args.model
    seed = args.seed

    gen = GradesGenerator(size=size, nb_grades=nb_grades,noise=noise,seed=seed)
    grades,admission = gen.generate_grades()
    gen.analyze_gen()

    if model == 'MR-Sort':
        MRSort_solv = MRSort_Solver(gen)
        MRSort_solv.set_constraint('MaxMin')
        MRSort_solv.solve()
        f1_score_, accuracy_, time_, error_count = MRSort_solv.get_results()
    else: 
        pass