# Test Generator

import sys
sys.path.append('./')

from generator import GradesGenerator

size = 100
nb_grades = 5
noise = 0
nb_class = 1

gen = GradesGenerator(size=size, nb_grades=nb_grades,noise=noise, nb_class=nb_class)
grades,admissions = gen.generate_grades()
gen.analyze_gen()

# Test MR-Sort
from models import MRSort_Solver, SAT_Solver

MRSort_solv = MRSort_Solver(gen)
MRSort_solv.set_constraint('MaxMin')
MRSort_solv.solve()
f1_score_, accuracy_, time_, error_count = MRSort_solv.get_results()

#Test SAT-Solver

#Simple case
print("\nSIMPLE CASE FOR SAT\n")
size = 100
nb_grades = 5
noise = 0
nb_class = 1

gen = GradesGenerator(size=size, nb_grades=nb_grades,noise=noise, nb_class=nb_class)
grades,admissions = gen.generate_grades()

SAT_Solv = SAT_Solver(generator=gen)
SAT_Solv.init_clauses(grades,admissions)
SAT_Solv.get_results(grades,admissions)

# Multi case
print()
print("\nMULTI CLASS FOR SAT\n")
size = 100
nb_grades = 5
noise = 0
nb_class = 8

gen = GradesGenerator(size=size, nb_grades=nb_grades,noise=noise, nb_class=nb_class)
grades,admissions = gen.generate_grades()

SAT_Solv = SAT_Solver(generator=gen)
SAT_Solv.init_clauses(grades,admissions)
SAT_Solv.get_results(grades, admissions)