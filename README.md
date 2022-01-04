# Project Système de décision

## Students

[Ariane Dalens](https://gitlab-student.centralesupelec.fr/ariane.dalens)   
[Lucas Sor](https://gitlab-student.centralesupelec.fr/lucas.sor)  
[Magali Morin](https://gitlab-student.centralesupelec.fr/2018morinm)

#### Due date
:calendar: **14/01/2021**
:calendar: **01/02/2021**

## :books: Subject of the project 

> To be redefined 

Consider a situation in which a committee for a higher education program has to decide about the admission of students on the basis of their evaluations in 4 courses: mathematics (M), physics (P), literature (L) and history (H). Evaluations on all courses range in the [0,20] interval. To be accepted (A) in the program, the committee considers that a student should obtain at least 12 on a “majority” of courses, otherwise, the student is refused (R). From the committee point of view, all courses (criteria) do not have the same importance. To define the required majority of courses, the committee attaches a weight wj ≥ 0 to each course such that they sum to 1; a subset of courses C ⊆ {M, P, L, H} is considered as a majority if j∈C wj ≥ λ, where λ ∈ [0, 1] is a required majority level.

To do so we will: 
1. implement an Inv-MR-Sort with a linear solver (gurobi) 
2. implement a Inv-NCS  with a SAT/MaxSAT solver

Our solutions will be evaluated based on: 
1. computational time
2. ability to learn a set of data and the ability to generalise 
3. adaptability to noisy data

## :runner: Running the code

```bash
python main
```

## :package: Organisation of the project

### Structure

```bash 
├── notebook
│   └── generator.ipynb
└── utils
│   └── helpers.py
├── tests
│   └── tests.py
├── MR-Sort-NCS.pdf
├── README.md
├── main.py
└── requirements.txt
```

### Requirements 
```bash
pip3 install -r requirements.txt 
```

``gurobipy==9.5.0``

## Theoretical Explanation 
> TODO: adding LaTeX equations and report 

## References 
[1] D. Bouyssou, T. Marchant, An axiomatic approach to noncompensatory sorting methods in MCDM, I: The case of two categories, European Journal of Operational Research, 178(1):217–245,(2007).  

[2] D. Bouyssou, T. Marchant, An axiomatic approach to noncompensatory sorting methods in MCDM, II: More than two categories, European Journal of Operational Research, 178(1):246–276, (2007). 

[3] Eda Ersek Uyanik, Vincent Mousseau, Marc Pirlot, and Olivier Sobrie. Enumerating and catego- rizing positive boolean functions separable by a k-additive capacity. Discrete Applied Mathematics, 229:17-30, (2017).  

[4] Agnes Leroy, Vincent Mousseau, and Marc Pirlot. Learning the parameters of a multiple criteria sorting method. Algorithmic Decision Theory, 219-233, (2011).  

[5] Belahcene K., Labreuche C., Maudet N., Mousseau V., and Ouerdane, W. An efficient SAT formu- lation for learning multiple criteria non-compensatory sorting rules from examples, Computers & Operations Research, 97, 58–71, (2018).  
