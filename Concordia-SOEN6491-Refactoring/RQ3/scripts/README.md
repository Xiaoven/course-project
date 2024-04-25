## Script Order

1. `process_refactorings.py`, `process_metrics.py`
2. `correlation.py`
3. update `columns_to_remove` in `model.py` according to the correlation (>0.8)
4. `model.py`
5. `analyze.py`, `count.py`


## Data to collect

### Refactoring
 $(relj, refk, C)$
 - $rel_j$ indicates the release number, 
 - $ref_k$ the kind of refactoring occurred
 - $C$ is the set of refactored classes

 Filter (potential false positive):
    - refactorings mapping between main and test files
    - ignore Move and Rename class for inner class
    - skip multiple classes in one java file
    - skip refactoring types applied less than 10 times on a system 
    - skip refactoring types which data size of classes is less than 10 times in a systems

### Metrics:
- Lines of Code (LOC): The number of lines of code excluding white spaces and comments
- Chidamber & Kemerer (CK) metrics
    - Weighted Methods per Class (WMC): 
        - The complexity of a class as the sum of the McCabe’s cyclomatic complexity of its methods 
    - Depth of Inheritance Tree (DIT): 
        - The depth of a class as the number of its ancestor classes
    - Number Of Children (NOC): 
        - The number of direct descendants (subclasses) of a class
    - Response for a Class (RFC): 
        - The number of distinct methods and constructors invoked by a class
    - Coupling Between Object (CBO): 
        - The number of classes to which a class is coupled
    - Lack of COhesion of Methods (LCOM):
        - The higher the pairs of methods in a class sharing at least a field, the higher its cohesion

## Steps
### Step 1. Spearman’s rank correlation (> 0.8)

The "dit" values in the JFreeChart dataset are identical, resulting in NaN values in Spearman’s correlation calculations. Given the lack of variability and meaningful insights from the "dit" column, we opt to remove it from the JFreeChart DataFrame.

Correlation:
- gson: None
- spring-security: None
- kafka: None



### Step 2. Construct logistic regression models

Normalization and correlation detection should be applied on the dataset.

$$
P(RefactoringA\ is\ performed\ on\ the\ system) = \pi (X_1, X_2, …, X_n) = \frac{e^{C_0+C_1X_1+…+C_nX_n}}{1 + e^{C_0+C_1X_1+…+C_nX_n}}
$$

- The dichotomous dependent variable: indicating whether or not a particular type of refactoring was performed

- the independent variables $X_i$ are the changes of quality metrics normalized through the z-score.

1. Normalize metrics using the z-score, i.e., by subtracting the mean and dividing by the standard deviation.
    - Z-score 可以将不同数据集之间的数据进行标准化，使其具有可比性
    - 分别针对每个metric的所有项目数据计算平均值和方差，并在每个metric上应用 Z-score，以了解每个metric的相对表现情况
2. Given a refactoring type $r_i$ and a system $s_j$, we build the two models presented above only if the refactoring type $r_i$ has been applied on the system $s_j$ at least 10 times. This is done to avoid the creation of unreliable logistic regression models.
    - count the frequencies of each refactoring type in each project


- Use substraction of metrics before and after refactoring application as X: too many zero values, cause LinAIgError: Singular matrix
- Use the ratio of metrics before and after application of reconstruction as X: Perfect separation is detected or prediction, parameters may not be identified. This is because we only have data for Y=1 (refactoring applied)
- use metrics after refactoring application as Y, and metrics before refactorings as X. However, logistic regression is a model used to handle binary classification problems, so the target variable Y should be a vector representing the binary classification results.


### Step 3. Compute Odds Ratio (OR)

$$
OR_i = e^{C_i}
$$

It means for every one-unit increase in $X_i$, the probability of the dependent variable occurring becomes $e_{Ci}$ times higher.