from gurobipy import *
import time
import numpy as np
from collections import Counter
from sklearn.metrics import f1_score


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
            print("Precision: {:.2f} %\n".format(accuracy_*100))
            print("F1-score:  {:.2f} %\n".format(f1_score_*100))
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
