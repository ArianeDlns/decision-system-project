import subprocess
import time
from utils.helpers import *

class SAT_Solver:
    def __init__(self, generator):
        """
        Initialize the solver
        """
        self.gen = generator
        self.grades, self.admission = generator.generate_grades()

        # Constants
        self.size = self.gen.size
        self.nb_grades = self.gen.nb_grades
        self.s = {x for x in range(self.nb_grades)}

        # time to solve
        self.time = None

        # ----- SAT variables ----
        #Variable alpha
        self.alpha = []
        for i in range(0,self.nb_grades):
            for k in range(0,21):
                self.alpha.append((i,k))

        self.v2i_alpha = {v : i+1 for i,v in enumerate(self.alpha)} # à chaque variable associe un nombre
        self.A = len(self.v2i_alpha)

        #Variable Beta
        self.subsets = list(powerset(self.s))
        self.v2i_beta = {v : self.A+i+1 for i,v in enumerate(self.subsets)}


    def init_clauses(self):
        """
        Initialize clauses
        """
        #Clause 1
        self.clause_1 = []
        for i in range(0,self.nb_grades):
            for k in range(0,21):
                for j in range(k+1,21):
                    self.clause_1.append([-self.v2i_alpha[(i,k)], self.v2i_alpha[(i,j)]])
        
        #Clause 2
        self.clause_2 = []
        for i in self.subsets:
            C_prime = set(i)
            for j in self.subsets:
                C = set(j)
                if C.issubset(C_prime):
                    self.clause_2.append((-self.v2i_beta[j], self.v2i_beta[i]))

        #Clause 3 : que pour les étudiants acceptés
        self.clause_3 = []
        for c in self.subsets:
            C = set(c)
            D = self.s.difference(C)
            j = tuple(D)
            self.alpha_c3 = []
            for k in range(0,21):
                for i in range(0,self.nb_grades):
                    if i in C:
                        self.alpha_c3.append(self.v2i_alpha[(i,k)])
            self.clause_3.append(self.alpha_c3+[self.v2i_beta[j]])

        #Clause 4 : que pour les étudiants refusés
        self.clause_4 = []
        for c in self.subsets:
            C = set(c)
            j = tuple(C)
            self.alpha_c4 = []
            for k in range(0,21):
                for i in range(0,self.nb_grades):
                    if i in C:
                        self.alpha_c4.append(-self.v2i_alpha[(i,k)])
            
            self.clause_4.append(self.alpha_c4+[-self.v2i_beta[j]])

    def solve(self):
        """
        Construction du DIMCS et Résolution
        """
        #DMICS
        self.i2v = {}
        for i in range(len(self.v2i_alpha)):
            self.i2v[i+1] = list(self.v2i_alpha.keys())[list(self.v2i_alpha.values()).index(i+1)]
        for i in range(len(self.v2i_beta)):
            self.i2v[i+1+self.A] = list(self.v2i_beta.keys())[list(self.v2i_beta.values()).index(i+1+self.A)]

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
            return True, [int(x) for x in model if int(x) != 0], {self.i2v[abs(int(v))] : int(v) > 0 for v in model if int(v)!=0} 
        
        #Resolution
        start = time.time()
        self.myClauses= self.clause_1 + self.clause_2 + self.clause_3 + self.clause_4
        self.myDimacs = clauses_to_dimacs(self.myClauses,len(self.v2i_alpha)+len(self.v2i_beta))
        write_dimacs_file(self.myDimacs,"./workingfile.cnf")
        self.res = exec_gophersat("./workingfile.cnf") 
        end = time.time()
        self.time = end - start
        print(self.time)
        print(self.res)      

    def get_results(self):
        """
        Print results of the solver
        Returns :
            f1_score_ (float): f1-score of the solution
            accuracy_ (float): accuracy of the solution
            time (float): time spent trying to find the optimum
            error_count (int): 1/0 based on if gurobi converges or not 
        """
        self.resultats = self.res[2]
        self.note_limite = []
        for i in range(0,self.nb_grades):
            for k in range(0,21):
                if self.res[2].get((i,k)) is True:
                    self.note_limite.append((i,k))

        self.ss_ensemble_matière = []
        for c in self.subsets:
            if self.res[2].get(c) is True:
                self.ss_ensemble_matière.append(c)

        results = []
        for self.etudiant in range(0,self.size):
            dico_note = {}
            for self.matiere in range (0, len(self.nb_grades)):
                if self.grades[self.etudiant, self.matiere] >= self.note_limite[self.matiere][1] : 
                    dico_note[self.matiere] = True

        pass


        