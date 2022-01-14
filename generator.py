import numpy as np
from collections import Counter


class GradesGenerator():
    def __init__(self, size: int = 100, nb_grades: int = 4, lbd: float = None, weights: np.ndarray = None, betas: np.ndarray = None, seed: int = None, noise: float = None, nb_class: int=None):
        self.noise = noise
        self.seed = seed
        if seed is None:
            self.seed = np.random.random_integers(1,100)
        self.size = size
        self.lbd = lbd
        self.nb_grades = nb_grades
        self.nb_class =  nb_class # This is the number of class, for accepted and rejected it is equal to 1 (Accepted) as the other students (Rejected) are automatically determined
        if nb_class is None:
            self.nb_class = 1
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
        if self.nb_class == 1: #Simple case
            betas = rng.integers(low=8, high=15, size=self.nb_grades)
        else: #Multi class case
            betas = [rng.integers(low=8, high=15, size=self.nb_grades)]
            for _ in range(self.nb_grades):
                last_boundary = betas[-1]
                new_boundary = []
                for last_low in (last_boundary):
                    new_boundary.append(rng.integers(low=last_low, high = 15))
                betas.append(new_boundary)
        return np.array(betas)

    def classifier(self, grades):
        """
        Classifies grades
        Returns :
               admissions (array<bool>) : True or False based on admission
        """
        # TODO: adding admission based on nb_class
        
        if self.nb_class == 1: # Only 1 class (Accepted) the other student are automatically rejected
            if self.noise > 0:
                #print('Adding {:.2f} % of noise'.format(self.noise*100)) 
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

        else: #Mutli class
            rng = np.random.default_rng(self.seed)
            if self.noise > 0:
                #print('Adding {:.2f} % of noise'.format(self.noise*100)) 
                admissions = []
                for grade in grades: 
                    tirage = np.random.binomial(1, self.noise)
                    if tirage:
                        admissions += [rng.integers(low=0, high = self.nb_class)] #Random class if tirage
                    else:
                        c = 0
                        while ((grade >= self.betas[c])*self.weights).sum() >= self.lbd and c < self.nb_class:
                            c += 1
                        admissions += [c]
                admissions = np.array(admissions)
            else: 
                admissions = []
                for grade in grades:
                    c = 0
                    while ((grade >= self.betas[c])*self.weights).sum() >= self.lbd and c < self.nb_class:
                        c += 1
                    admissions += [c]
                admissions = admissions = np.array(admissions)
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
        d = dict(Counter(admissions))
        print(f"Got-in: {d}")

        percentage = {}
        for key in d.keys():
            percentage[key] = d[key] / sum(list(d.values())) *100 * 100//100
        print(f"% Got-in: {percentage} %")
        print('--------------------------')
