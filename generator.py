import numpy as np
from collections import Counter


class GradesGenerator():
    def __init__(self, size: int = 100, nb_classes: int = 1, nb_grades: int = 4, lbd: float = None, weights: np.ndarray = None, betas: np.ndarray = None, seed: int = None, noise: float = None):
        self.noise = noise
        self.seed = seed
        if seed is None:
            self.seed = np.random.random_integers(1,100)
        self.size = size
        self.lbd = lbd
        self.nb_classes = nb_classes
        self.nb_grades = nb_grades
        if lbd is None:
            rng = np.random.default_rng(self.seed)
            self.lbd = rng.uniform(0.2, 0.8)
        self.weights = weights
        if weights is None:
            self.weights = self.generate_weights()
        self.betas = betas
        if betas is None:
            self.betas = self.generate_betas()
        if noise is None:
            rng = np.random.default_rng(self.seed)
            self.noise = rng.uniform(0.01, 0.1)

    def generate_weights(self):
        """
        Generate weights based on a normal distribution
        Returns :
               weights (array<float>) : weights between 0 and 1 
        """
        rng = np.random.default_rng(self.seed)
        weights = abs(rng.standard_normal(self.nb_grades))
        weights /= weights.sum()
        return weights

    def generate_betas(self):
        """
        Generate betas between 8 and 15 based on a uniform distribution
        Returns :
               betas (array<int>) : frontiers of grade
        """
        rng = np.random.default_rng(self.seed)
        betas = rng.integers(low=8, high=15, size=self.nb_grades)
        return np.array(betas)

    def classifier(self, grades):
        """
        Classifies grades
        Returns :
               admissions (array<bool>) : True or False based on admission
        """
        if self.noise > 0:
            print('Adding {:.2f} % of noise'.format(self.noise*100)) 
            admissions = []
            for grade in grades: 
                tirage = np.random.binomial(1, self.noise)
                if tirage:
                    admissions += [((grade >= self.betas)*self.weights).sum() <= self.lbd]
                else:
                    admissions += [((grade >= self.betas)*self.weights).sum() >= self.lbd]
            admissions = np.array(admissions)
        else: 
            admissions = np.array([((grade >= self.betas)*self.weights).sum() >= self.lbd for grade in grades])
        return admissions

    def generate_grades(self):
        """
        Generate grades based on a uniform distribution between 0 and 20 
        Returns :
              grades (array<array<int>>) : grades of students
              admissions (array<bool>) : True or False based on admission
        """
        rng = np.random.default_rng(self.seed)
        grades = rng.integers(low=0, high=21, size=(self.size, self.nb_grades))
        admissions = self.classifier(grades)
        return grades, admissions
    
    def analyze_gen(self):
        """
        Analyze the generator
        Returns :
            None
        """
        print('---------Analyze----------')
        print(f"Lambda: {self.lbd}")
        print(f"Weights: {self.weights}")
        print(f"Betas: {self.betas}")
        grades, admissions = self.generate_grades()
        print(f"Got-in: {dict(Counter(admissions))}")
        print("% Got-in: {:.2f} %".format(admissions.sum()/self.size))
        print('--------------------------')
        pass
