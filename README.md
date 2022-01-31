# Project Système de décision

## Students

[Ariane Dalens](https://gitlab-student.centralesupelec.fr/ariane.dalens)   
[Lucas Sor](https://gitlab-student.centralesupelec.fr/lucas.sor)  
[Magali Morin](https://gitlab-student.centralesupelec.fr/2018morinm)

#### Due date
:calendar: **14/01/2021**  
:calendar: **01/02/2021**

## :books: Subject of the project 

> Consider a situation in which a committee for a higher education program has to decide about the admission of students on the basis of their evaluations in 4 courses: mathematics ($`M`$), physics ($`P`$), literature ($`L`$) and history ($`H`$). Evaluations on all courses range in the $`[0,20]`$ interval. To be accepted ($`A`$) in the program, the committee considers that a student should obtain at least 12 on a “majority” of courses, otherwise, the student is refused ($`R`$). From the committee point of view, all courses (criteria) do not have the same importance. To define the required majority of courses, the committee attaches a weight $`w_j ≥ 0`$ to each course such that they sum to 1; a subset of courses $`C ⊆ {M, P, L, H}`$ is considered as a majority if $`\forall j∈C`$ $`w_j ≥ λ`$, where $`λ ∈ [0, 1]`$ is a required majority level.

**To solve this problem we will implement:**
1. an Inv-MR-Sort with a linear solver (gurobi) 
2. a Inv-NCS  with a SAT/MaxSAT solver

Our solutions will be evaluated based on: 
1. computational time
2. ability to learn a set of data and the ability to generalise 
3. adaptability to noisy data

## :runner: Running the code

```bash
python3 tests/tests.py # To run tests
python main.py # To run the full module with default arguments
python3 main.py --size 150 --nb_grades 3 --nb_class 1 --noise 0 --model MILP --seed 99 # With specific arguments 
```

**Arguments**:
- ``--size`` : (default=150) - number of students graded
- ``--nb_grades`` : (default=3) - number of grades
- ``--nb_class`` : (default=1) - number of classes
- ``--noise`` : (default=0) - proportion of noisy data
- ``--model`` : (default=MR-Sort) - model used either MILP or SAT
- ``--seed`` : (default=None) - seed used 

### Performances 
**1. Impact of the nb_grades**

**Accuracy and f1-score for MILP on 100 students**           |  **Timing for MILP on 100 students**  
:-------------------------:|:-------------------------:
![alt text](img/scores_MR-Sort.png?raw=true "scores_MR-Sort") |  ![alt text](img/time_MR-Sort.png?raw=true "time_MR-Sort")
**Accuracy and f1-score for SAT on 100 students**           |  **Timing for SAT on 100 students**  
![alt text](img/scores_SAT.png?raw=true "scores_SAT") |  ![alt text](img/time_SAT.png?raw=true "time_SAT")

**2. Impact of the noise**  

**Accuracy and f1-score for MILP on 100 students and 3 grades**           |  **Timing for MILP on 100 students and 3 grades**  
:-------------------------:|:-------------------------:
![alt text](img/scores_MR-Sort_noisy.png?raw=true "scores_MR-Sort") |  ![alt text](img/time_MR-Sort_noisy.png?raw=true "time_MR-Sort")
**Accuracy and f1-score for SAT on 100 students and 3 grades**           |  **Timing for SAT on 100 students and 3 grades**  
![alt text](img/scores_SAT_noisy.png?raw=true "scores_SAT") |  ![alt text](img/time_SAT_noisy.png?raw=true "time_SAT")

**3. Impact of the multi class**  

**Accuracy and f1-score for SAT on 150 students and 3 grades**           |  **Timing for SAT on 150 students and 3 grades**  
:-------------------------:|:-------------------------:
![alt text](img/scores_SAT_multi.png?raw=true "scores_SAT") |  ![alt text](img/time_SAT_multi.png?raw=true "scores_SAT")

## :package: Organisation of the project

### Structure

```bash 
.
├── MR-Sort-NCS.pdf # Subject of the project
├── README.md
├── gophersat # Solver MacOSx (Monterey)
├── gophersat.exe # Solver Windows
├── generator.py # Generator class
├── main.py # Entry point
├── models.py # Models class
├── img/ # Results in .png
├── notebook
│   ├── SolveurSAT.ipynb
│   ├── generator.ipynb
│   └──testing_performances.ipynb # Testing performances of the MR-Sort solver
├── requirements.txt
├── tests
│   └── tests.py  # Testing
└── utils
    ├── argument.py # Handeling arguments
    └── helpers.py
```

### Requirements 
```bash
pip3 install -r requirements.txt 
```
``gurobipy==9.5.0``

## :heavy_division_sign: Theoretical Explanation 


The problem statement is as follows : 

We consider two sets of students $`A`$ (accepted) and $`R`$ (rejected) and that the coalitions of criteria are represented using additive weights $`w_j`$ and a majority threshold $`\lambda`$. That is to say that students are accepted if and only if the sum of the weight of their courses in which they obtain at least the minimum required mark is a majority (greater or equal to $`\lambda`$).

Our goal is to find the weight vector $`w`$ and the threshold $`\lambda`$ using linear programming and SAT solvers.

Let $`b = (b_1, \dots, b_n)`$ the different minimal grades that one student must have to pass some course i.e. student $`s`$ passes course $`i \in \llbracket 1, n \rrbracket`$ if and only if his grade at course i noted $`s_i`$ is such that $`s_i \geq b_i`$. 

We can now define a boolean variable $`\delta_i(s)`$ such that $`\delta_i(s) = 0`$ if the student fails course $`i`$ nad $`\delta_i(s) = 1`$ if student passes course $`i`$. This can be summed up with the formula 
```math
\forall s,i \quad \delta_i(s) = 1 \Leftrightarrow s_i \geq b_i
```

In order to put this behavior in a linear programming algorithm we can proceed as follows. We consider an arbitrarily large number $`M`$ and add the condition 

```math
M(\delta_i(s) - 1) \leq s_i - b_i < M\delta_i(s)
```

However, as computers don't really like strick inequalities we can change our condition with :
```math
M(\delta_i(s) - 1) \leq s_i - b_i \leq M\delta_i(s) - \varepsilon
```

where $`\varepsilon`$ is a small number.


Now that we have defined the boolean variables $`\delta_i(s)`$, we can use them to define continuous variables $`w_i(s)`$ for each course $`i`$ and for each student $`s`$ such that :

```math 
w_i(s) = 
\left\{ 
    \begin{array}{l} 
        w_i, \text{ if } s_i \geq b_i \\
        0, \text{ otherwise}
    \end{array}
\right.
```

We remind ourselves that the $`w_i`$ are the weights attributed to course $`i`$ and that it is our goal to find them.

In order to introduce the behavior of this new variable in our linear programming algorithm we can add the following conditions :

```math
\left\{ 
    \begin{array}{l} 
        w_i \geq w_i(s) \geq 0 \\
        \delta_i(s) \geq w_i(s) \geq \delta_i(s) + w_i - 1
    \end{array}
\right.
```

Now, the only thing left to define for our linear programming algorithm is the function to maximize. Here we consider the "prediction margin" for each student $`s`$ noted $`\sigma_s`$ such that :

```math
\left\{ 
    \begin{array}{l} 
        \forall s \in A, \quad \sum w_i(s) - \lambda - \sigma_s = 0 \\
        \forall s \in R, \quad \sum w_i(s) - \lambda + \sigma_s = -\varepsilon'
    \end{array}
\right.
```
    
where $`\varepsilon'`$ is another small positive number. 

$`\sigma_s`$ is such that it is the positive difference between the student's sum of weight and the margin. That means that in order to have a good model and find good $`w`$ and $`\lambda`$, we must maximize the sum of all $`\sigma_s`$.

To sum up, the linear programming algorithm that will allow us to find the weight vector $`w`$ and the threshold $`\lambda`$ is described by :

```math 
\text{Max} \sum_s \sigma_s
```

```math
\begin{array}{l l}
    \text{subject to} & M(\delta_i(s) - 1)  \leq s_i - b_i \leq M\delta_i(s) - \varepsilon \\
    & w_i \geq w_i(s) \geq 0 \\
    & \delta_i(s) \geq w_i(s) \geq \delta_i(s) + w_i - 1 \\
    & \forall s \in A, \quad \sum w_i(s) - \lambda - \sigma_s = 0 \\
    & \forall s \in R, \quad \sum w_i(s) - \lambda + \sigma_s = -\varepsilon' \\
    \\
    \text{where} & \delta_i(s) \in \{0,1\} \\
    & w_i(s) \in [0, 1 ] \\
    & \sigma_s \in [0, 1] \\
    & w_i \in [0, 1] \\
    & \lambda \in [0,1]
\end{array}
```

Now, let's take a different approach. Rather than using the linear programming algorithm method, let's use the SAT-solver method.

Let $`\alpha_{ki}`$ a boolean variable that is true if and only if the evaluation $`k`$ on criterion $`i`$ is above the frontier and $`\beta_C`$ a boolean variable that is true if and only if the coalition of criteria is a majority.

To ensure that every evaluations that are ranked above a "good" evaluation are also good, our SAT-solver should satisfy the following clause : 

```math
\forall k' > k, \quad \alpha_{ki} \Rightarrow \alpha_{k'i} \text{ i.e. } \neg \alpha_{ki} \lor \alpha_{k'i}
```

In the same way, if one coalition of criteria is a majority, all coalitions of criteria that include it should also be majorities.

```math
\forall C \subset C', \quad \beta_C \Rightarrow \beta_{C'} \text{ i.e. } \neg \beta_C \lor \beta_{C'}
```

Now, for all students that are accepted, we should write clauses that state it. Those clauses are in the form :

```math
\forall C \subset \mathcal{N}, \quad \bigwedge\limits_{i \in C} \neg \alpha_{ki} \Rightarrow \beta_{\mathcal{N}\setminus C} \text{ i.e. }  \bigvee\limits_{i \in C} \alpha_{ki} \lor \beta_{\mathcal{N}\setminus C}
```

This means that the criteria in the coalition $`C`$ are not necessary to be a majority.

In the same way, for all students that are rejected, we also should write clauses stating it. Those clauses are in the form :

```math
\forall C \subset \mathcal{N}, \quad \bigwedge\limits_{i \in C} \alpha_{ki} \Rightarrow \neg \beta_{C} \text{ i.e. }  \bigvee\limits_{i \in C} \neg \alpha_{ki} \lor \neg \beta_{C}
```

This means that the criteria in the coalition $`C`$ are not sufficient to be a majority.

Now, let's get into the case where there are no longer two end classes ($`A`$ and $`R`$) but an arbitrary number ($`H`$). We can derive a SAT formulation of this problem from the simpler one we described before. Let the index $`h`$
 describe the end profile index and $`\alpha_{kih}`$ the boolean variable that is true if on criterion $`i`$, the value $`k`$ is sufficient at level $`h`$.

We can adapt the four clauses :


The ascending scales clause : 

```math
\forall k' > k, \quad \alpha_{kih} \Rightarrow \alpha_{k'ih} \text{ i.e. } \neg \alpha_{kih} \lor \alpha_{k'ih}
```


The coalitions strength clause :

```math
\forall C \subset C', \quad \beta_C \Rightarrow \beta_{C'} \text{ i.e. } \neg \beta_C \lor \beta_{C'}
```


The outranking of alternatives by boudary below them :
```math
\forall C \subset \mathcal{N}, \quad \forall h \in H, \quad  \bigvee\limits_{i \in C} \alpha_{a_i ih} \lor \beta_{\mathcal{N}\setminus C}
```

The outranking of alternatives by boundary above them :

```math
\forall C \subset \mathcal{N}, \quad \forall h \in H, \quad  \bigvee\limits_{i \in C} \neg \alpha_{u_i ih} \lor \neg \beta_{C}
```

And finally we add another clause that will define the hierarchy of profiles amongst the different end results $`h`$.

```math
\forall h'>h, \quad \neg \alpha_{kih} \Rightarrow \neg \alpha_{kih'} \text{ i.e. } \alpha_{kih} \lor \neg \alpha_{kih'}
```

## References 
[1] D. Bouyssou, T. Marchant, An axiomatic approach to noncompensatory sorting methods in MCDM, I: The case of two categories, European Journal of Operational Research, 178(1):217–245,(2007).  

[2] D. Bouyssou, T. Marchant, An axiomatic approach to noncompensatory sorting methods in MCDM, II: More than two categories, European Journal of Operational Research, 178(1):246–276, (2007). 

[3] Eda Ersek Uyanik, Vincent Mousseau, Marc Pirlot, and Olivier Sobrie. Enumerating and catego- rizing positive boolean functions separable by a k-additive capacity. Discrete Applied Mathematics, 229:17-30, (2017).  

[4] Agnes Leroy, Vincent Mousseau, and Marc Pirlot. Learning the parameters of a multiple criteria sorting method. Algorithmic Decision Theory, 219-233, (2011).  

[5] Belahcene K., Labreuche C., Maudet N., Mousseau V., and Ouerdane, W. An efficient SAT formu- lation for learning multiple criteria non-compensatory sorting rules from examples, Computers & Operations Research, 97, 58–71, (2018).  

[6] A. Leroy, V. Mousseau, and M. Pirlot, ‘Learning the parameters of a multiple criteria sorting method’, in International Conference on Algorithmic Decision Theory, pp. 219–233. Springer, (2011).   

[7] J. Berg, M. Järvisalo, R. Martins, Advances in Maximum Satisfiability, ECAI’20 Online, September 4, 2020.  

[8] A. Tlili, K. Belahcène, O. Khaled, V. Mousseau, W. Ouerdane, Learning Non-Compensatory Sorting models using efficient SAT/MaxSAT formulations, European Journal of Operational Research, August 2021  
