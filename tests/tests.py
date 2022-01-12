# test Generator
import sys
sys.path.append('./')

from generator import GradesGenerator

size = 100
nb_grades = 10

gen = GradesGenerator(size=size, nb_grades=nb_grades)
grades,admission = gen.generate_grades()
print(f"Lambda: {gen.lbd}")
print(f"Weights: {gen.weights}")
print(f"Betas: {gen.betas}")
print(f"Betas: {admission}")
print(f"Admission: {admission.sum()/len(admission)}")
