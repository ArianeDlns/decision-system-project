from gurobipy import *
import time
import numpy as np
from collections import Counter
from sklearn.metrics import f1_score, accuracy_score
from itertools import chain
from itertools import combinations
import subprocess


MAX_GRADE = 21

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


class MRSort_Solver:
    def __init__(self, generator, epsilon: float = 1e-6, M: int = 1e2):
        """
        Initialize the solver
        """
        self.gen = generator
        self.grades, self.admission = generator.generate_grades()
        self.model = Model("MR-sort")

        # Constants
        self.size = self.gen.size
        self.nb_grades = self.gen.nb_grades
        self.epsilon = epsilon
        self.M = M

        # time to solve
        self.time = None

        # ----- Gurobi variables ----
        self.obj = self.model.addVar()  # Sum(Sigma_s) objective
        # sigmas for each student (in A*)
        self.A = self.model.addMVar(shape=self.size, lb=0, ub=0.5)
        # sigmas for each student (in R*)
        self.R = self.model.addMVar(shape=self.size, lb=0,  ub=0.5)

        # weights
        self.weights = self.model.addMVar(shape=self.nb_grades, lb=0, ub=1)
        # betas
        self.betas = self.model.addMVar(shape=(self.nb_grades))
        # lambda
        self.lbd = self.model.addVar(lb=0.1, ub=1)

        # student weights
        self.weights_ = self.model.addMVar(
            shape=(self.size, self.nb_grades), lb=0, ub=1)
        # delta
        self.deltas = self.model.addMVar(
            shape=(self.size, self.nb_grades), vtype=GRB.BINARY)

    def set_constraint(self, objective):
        """
        Set the contraints of the model, please refer to the README.md for more details
        """

        # Margins in A*
        self.model.addConstrs((
            quicksum(self.weights_[j, i] for i in range(
                self.nb_grades)) - self.lbd - self.A[j] == 0
        ) for j in range(self.size) if self.admission[j] == True
        )

        # Margins in R*
        self.model.addConstrs((
            quicksum(self.weights_[j, i] for i in range(
                self.nb_grades)) - self.lbd + self.R[j] == - self.epsilon
        ) for j in range(self.size) if self.admission[j] == False
        )

        # Grades and betas-frontiers
        self.model.addConstrs((
            (self.M*(self.deltas[j, :] - np.ones(self.nb_grades)) <= self.grades[j, :] - self.betas))
            for j in range(self.size))

        self.model.addConstrs((
            self.grades[j, :] - self.betas <= self.M*self.deltas[j, :] - self.epsilon*np.ones(self.nb_grades))
            for j in range(self.size))

        # Weights constraint
        self.model.addConstrs((
            self.weights >= self.weights_[j])
            for j in range(self.size)
        )

        # Weights sum equals 1
        self.model.addConstr(
            quicksum(self.weights[k] for k in range(self.nb_grades)) == 1)

        # Delta constraints
        self.model.addConstrs((
            self.deltas[j] >= self.weights_[j])
            for j in range(self.size)
        )

        self.model.addConstrs((
            self.weights_[j] >= self.deltas[j] + self.weights - np.ones(self.nb_grades))
            for j in range(self.size)
        )

        if objective == 'MaxMin':
            # Objective is the min margin
            self.model.addConstrs((self.obj <= self.A[j]) for j in range(
                self.size) if self.admission[j] == True)
            self.model.addConstrs((self.obj <= self.R[j]) for j in range(
                self.size) if self.admission[j] == False)
        elif objective == 'Sum':
            # Objective is the sum of margins in A* and R*
            self.model.addConstr(self.obj == quicksum(self.A[j] for j in range(self.size) if self.admission[j] == True)
                                 + quicksum(self.R[j] for j in range(self.size) if self.admission[j] == False))
        else:
            print('Error objective should be MaxMin or Sum')

    def solve(self):
        """
        Solve the model
        """
        start = time.time()
        self.model.update()
        self.model.setObjective(self.obj, GRB.MAXIMIZE)
        self.model.params.outputflag = 0  # 0 means without verbose
        self.model.optimize()
        end = time.time()
        self.time = end - start

    def get_results(self):
        """
        Print results of the solver
        Returns :
            f1_score_ (float): f1-score of the solution
            accuracy_ (float): accuracy of the solution
            time (float): time spent trying to find the optimum
            error_count (int): 1/0 based on if gurobi converges or not 
        """
        try:
            results = ((self.grades > self.betas.X) *
                       self.weights.X).sum(axis=1) > self.lbd.X
            f1_score_ = f1_score(self.admission, results)
            accuracy_ = sum([results[i] == self.admission[i]
                            for i in range(len(results))])/len(results)

            print(f"results:\n")
            print(f"Objective: {self.obj.X}")
            print(f"Lambda: {self.lbd.X}")
            print(f"Weights: {self.weights.X}")
            print(f"Betas: {self.betas.X}")
            print(f"Results: {dict(Counter(results))}")
            print("Precision: {:.2f} %".format(accuracy_*100))
            print("F1-score:  {:.2f} %".format(f1_score_*100))
            error_count = 0
            return f1_score_, accuracy_, self.time, error_count

        except GurobiError:
            print("WARNING: Gurobi didn't find a solution")
            error_count = 1
            return 0, 0, 0, error_count

    def check_constraint(self):
        """
        Check if contraints are respected - debug function
        """
        # Margins in A* == 0
        print([(sum(self.weights_.X[j, i] for i in range(self.nb_grades)) - self.lbd.X -
              self.A.X[j]) == 0 for j in range(self.size) if self.admission[j] == True])
        # Margins in R* == -epsilon
        print([(sum(self.weights_.X[j, i] for i in range(self.nb_grades)) - self.lbd.X + self.R.X[j])
              == - self.epsilon for j in range(self.size) if self.admission[j] == False])

        # Grades and beta frontier >= 0
        print([-(self.M*(self.deltas.X[j, :] - np.ones(self.nb_grades)) -
              self.grades[j, :] + self.betas.X) >= 0 for j in range(self.size)])
        print([-(self.grades[j, :] - self.betas.X - self.M*self.deltas.X[j, :] +
              self.epsilon*np.ones(self.nb_grades)) >= 0 for j in range(self.size)])

        # Weights constraint >=0 (=0 ou 1)
        print([(self.weights.X - self.weights_.X[j])
              >= 0 for j in range(self.size)])

        # Delta constraints >=0
        print([(self.deltas.X[j] - self.weights_.X[j])
              >= 0 for j in range(self.size)])
        print([(self.weights_.X[j] - self.deltas.X[j] - self.weights.X +
              np.ones(self.nb_grades)) >= 0 for j in range(self.size)])

class SAT_Solver:

    
    
    def __init__(self, generator):
        """
        Initialize the solver
        """
        self.generator = generator
        pass

    def init_clauses(self,grades,admissions):
        """
        Initialize clauses with the grades and the admissions
        """
            

        if self.generator.nb_class == 1: #Simple case 

            admissions = admissions.astype(int)

            #Variable alpha
            alpha = []
            for i in range(self.generator.nb_grades):
                for k in range(MAX_GRADE):
                    alpha.append((i,k)) # ==> donne tous les alpha i k 
            #Dictionnaire alpha
            v2i_alpha = {v : i+1 for i,v in enumerate(alpha)} # à chaque variable associe un nombre
            A = len(v2i_alpha)
            
                 

            #L'ensemble des subset 
            s = frozenset({i for i in range(self.generator.nb_grades)})
            subsets = list(powerset(s)) 


            #Dictionnaire beta
            v2i_beta = {frozenset(v) : A+i+1 for i,v in enumerate(subsets)}

            #Clause 1
            clause_1 = []

            for i in range(self.generator.nb_grades):
                for k in range(MAX_GRADE-1):
                    for j in range(k+1,MAX_GRADE):
                        clause_1.append([-v2i_alpha[(i,k)], v2i_alpha[(i,j)]])

            #Clause 2
            clause_2 = []

            for i in subsets:
                C_prime = frozenset(i)
                for j in subsets:
                    C = frozenset(j)
                    if C.issubset(C_prime) and C != C_prime:
                        clause_2.append([-v2i_beta[C], v2i_beta[C_prime]])

            #Clause 3

            clause_3 = []
            for st_idx,student in enumerate(grades):
                if admissions[st_idx] == 1:
                    for c in subsets:
                        alpha = []
                        for i in c:
                            alpha.append(v2i_alpha[(i,student[i])])
                    
                        clause_3.append(alpha+[v2i_beta[frozenset(s.difference(c))]])

            #Clause 4

            clause_4 = []


            for st_idx,student in enumerate(grades):
                if admissions[st_idx] == 0:
                    for c in subsets:
                        alpha = []
                        for i in c:
                            alpha.append(-v2i_alpha[(i,student[i])])
                    
                        clause_4.append(alpha+[-v2i_beta[frozenset(c)]])

            self.clause = clause_1 + clause_2 + clause_3 + clause_4
            self.i2v = get_i2v(v2i_alpha,v2i_beta,A)

        

        else: #Multi class case
            #Variable alpha
            alpha = []
            for i in range(self.generator.nb_grades):
                for k in range(MAX_GRADE):
                    for h in range(self.generator.nb_class+1):
                        alpha.append((i,k,h)) # ==> donne tous les alpha i k h

            #Dictionnaire alpha
            v2i_alpha = {v : i+1 for i,v in enumerate(alpha)} # à chaque variable associe un nombre
            A = len(v2i_alpha)

            #Créer l'ensemble des subset 

            #L'ensemble des subset 
            s = frozenset({i for i in range(self.generator.nb_grades)})
            subsets = list(powerset(s)) 


            #Dictionnaire beta
            v2i_beta = {frozenset(v) : A+i+1 for i,v in enumerate(subsets)}

            clause_1 = []

            for i in range(self.generator.nb_grades):
                for k in range(MAX_GRADE-1):
                    for h in range(self.generator.nb_class):
                        for j in range(k+1,MAX_GRADE):
                            clause_1.append([-v2i_alpha[(i,k,h)], v2i_alpha[(i,j,h)]])

            clause_2 = []

            for i in subsets:
                C_prime = frozenset(i)
                for j in subsets:
                    C = frozenset(j)
                    if C.issubset(C_prime) and C != C_prime:
                        clause_2.append([-v2i_beta[C], v2i_beta[C_prime]])

            clause_3 = []


            clause_3 = []
            for st_idx,student in enumerate(grades):
                for c in subsets:
                    alpha = []
                    for i in c:
                        alpha.append(v2i_alpha[(i,student[i],admissions[st_idx])])
                
                    clause_3.append(alpha+[v2i_beta[frozenset(s.difference(c))]])


            clause_4 = []

            for st_idx,student in enumerate(grades):
                if admissions[st_idx] < self.generator.nb_class:
                    for c in subsets:
                        alpha = []
                        for i in c:
                            alpha.append(-v2i_alpha[(i,student[i],admissions[st_idx]+1)])
                    
                        clause_4.append(alpha+[-v2i_beta[frozenset(c)]])

            clause_5 = []

            for k in range(MAX_GRADE):
                for i in range(self.generator.nb_grades):
                    for h in range(self.generator.nb_class):
                        for j in range(h+1, self.generator.nb_class+1):
                            clause_5.append([v2i_alpha[(i,k,h)],-v2i_alpha[(i,k,j)]])

            self.clause = clause_1 + clause_2 + clause_3 + clause_4 + clause_5
            self.i2v = get_i2v(v2i_alpha,v2i_beta,A)




                




    def solve(self):
        """
        Solve SAT clauses
        """
        def clauses_to_dimacs(clauses,numvar) :
            dimacs = 'c This is it\np cnf '+str(numvar)+' '+str(len(clauses))+'\n'
            for clause in clauses :
                for atom in clause :
                    dimacs += str(atom) +' '
                dimacs += '0\n'
            return dimacs

        def write_dimacs_file(dimacs, filename):
            with open(filename, "w", newline="") as cnf:
                cnf.write(dimacs)

        def exec_gophersat(filename, cmd = "./gophersat.exe", encoding = "utf8") :
            result = subprocess.run([cmd, filename], stdout=subprocess.PIPE, check=True, encoding=encoding)
            string = str(result.stdout)
            lines = string.splitlines()

            if lines[1] != "s SATISFIABLE":
                return False, [], {}

            model = lines[2][2:].split(" ")

            return True, [int(x) for x in model if int(x) != 0], { self.i2v[abs(int(v))] : int(v) > 0 for v in model if int(v)!=0} 

        myClauses= self.clause
        myDimacs = clauses_to_dimacs(myClauses,len(self.i2v))

        write_dimacs_file(myDimacs,"./SAT_Solver.cnf")
        t0 = time.time()
        res = exec_gophersat("./SAT_Solver.cnf")
        t1 = time.time()
        
        return res[-1], t1-t0

    def get_results(self,grades,admissions):
        """
        Print results of the solver
        Returns :
            f1_score_ (float): f1-score of the solution
            accuracy_ (float): accuracy of the solution
            time (float): time spent trying to find the optimum
            error_count (int): 1/0 based on if gurobi converges or not 
        """
            
        
        d,t = self.solve()
        

        if self.generator.nb_class == 1 :
            admissions = admissions.astype(int)
            predicted = []
            for student in grades:
                validated_courses = set()
                for i,k in enumerate(student):
                    if d[(i,k)]:
                        validated_courses.add(i)
                validated_courses = frozenset(validated_courses)
                if d[validated_courses]:
                    predicted.append(1)
                else:
                    predicted.append(0)
            predicted


            accuracy_ = accuracy_score(admissions,predicted)
            f1_score_ = f1_score(admissions,predicted, average='macro')
            error_rate = sum(admissions != predicted)
        else:
            predicted = []
            for student in grades:
                current_class = 0
                for h in range(self.generator.nb_class+1):
                    current_class = h
                    validated_courses = set()
                    for i,k in enumerate(student):
                        if d[(i,k,h)]:
                            validated_courses.add(i)
                    validated_courses = frozenset(validated_courses)
                    if validated_courses in d.keys():
                        if d[validated_courses]:
                            continue
                        else:
                            break
                    else:
                        break
                predicted.append(current_class-1)

            predicted

            accuracy_ = accuracy_score(admissions,predicted)
            f1_score_ = f1_score(admissions,predicted, average='macro')
            error_rate = sum(admissions != predicted)

        print("Runed in: {:.2f} seconds ".format(t))
        print("Precision: {:.2f} %".format(accuracy_*100))
        print("F1-score:  {:.2f} %".format(f1_score_*100))
        print(f"Error rate: {error_rate} errors")
        

        return f1_score_,accuracy_,t, error_rate
                    

        
