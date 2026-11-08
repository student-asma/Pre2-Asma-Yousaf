# Task 08: Non-Linear and Tree-Based Classification (KNN, Decision Tree, Random Forest)

## 1. Task Overview and Objectives
Task 08 explores non-linear, instance-based, and partition-based machine learning paradigms for large-scale multi-class text categorization. We evaluate three distinct architectures:
1. K-Nearest Neighbors (KNN): Non-parametric instance-based metric learning.
2. Decision Tree Classifier: Hierarchical axis-aligned recursive partitioning with pre-pruning.
3. Random Forest Classifier: Parallel ensemble bagging (Bootstrap Aggregation) combining 100 decorrelated decision trees.

The primary academic goal is to investigate how the Curse of Dimensionality and axis-orthogonal splits affect generalization in a 5,020-dimensional lexical feature space.

---

## 2. GitHub Folder Contents
Place the following three Jupyter Notebooks inside this task directory on GitHub:
- `Model_Training_KNN_News_100k.ipynb`
- `Model_Training_Decision_Tree_News_100k.ipynb`
- `Model_Training_Random_Forest_News_100k.ipynb`

### Associated Artifacts and Model Files
- `knn_model.joblib`
- `decision_tree_model.joblib`
- `random_forest_model.joblib`
- Dataset: `X_train_hybrid.npz`, `X_test_hybrid.npz`, `y_train.npy`, `y_test.npy`

---

## 3. Theoretical Architecture and Mathematical Formulations

### 3.1 K-Nearest Neighbors (KNN) and the Curse of Dimensionality
KNN predicts class labels via majority vote among the $K=5$ nearest neighbors. Due to metric concentration in high dimensions ($D=5,020$), standard Euclidean distance suffers from the distance concentration effect:

$$\lim_{D \to \infty} \frac{\text{dist}_{\max} - \text{dist}_{\min}}{\text{dist}_{\min}} \to 0$$

All document vectors become nearly equidistant. To mitigate this, we employed Cosine Distance:

$$\text{Cosine Similarity}(u, v) = \frac{u \cdot v}{\|u\|_2 \|v\|_2}$$

Despite cosine metric normalization, sparse vectors have minimal coordinate overlap, limiting KNN test accuracy to 44.06%.

### 3.2 Decision Tree Classifier: Recursive Partitioning & Overfitting Control
Decision trees recursively partition feature space to maximize Information Gain based on Gini Impurity:

$$\text{Gini}(t) = 1 - \sum_{k=1}^{K} p(k \mid t)^2$$

Text classification presents a severe challenge for unconstrained trees:
- An unpruned tree grows until leaves are pure, achieving 99.8% training accuracy but dropping to ~58% test accuracy (catastrophic memorization of document-specific n-grams).
- We resolved this via pre-pruning: `max_depth=30`, `min_samples_split=10`, `min_samples_leaf=5`, stabilizing test accuracy at 69.10%.

### 3.3 Random Forest Classifier: Bagging & Feature Subspace Sampling
Random Forest aggregates $B = 100$ independent decision trees:

$$\hat{y}(x) = \text{mode}\left\{ T_1(x), T_2(x), \dots, T_B(x) \right\}$$

Two-fold stochasticity reduces variance without increasing bias:
1. Bootstrap Sample: Each tree is trained on an independent sample with replacement ($N=80,000$).
2. Subspace Sampling: At each node split, only $m = \sqrt{D} \approx \sqrt{5,020} \approx 71$ candidate features are evaluated, decorrelating the individual trees.

---

## 4. Hyperparameter Configurations

| Model | Hyperparameter Configuration | Rationale |
| :--- | :--- | :--- |
| KNN | `n_neighbors=5`, `metric='cosine'`, `weights='distance'` | Mitigates metric distortion via inverse distance weighting. |
| Decision Tree | `criterion='gini'`, `max_depth=30`, `min_samples_split=10`, `min_samples_leaf=5` | Explicit pre-pruning to arrest deep noisy branching. |
| Random Forest | `n_estimators=100`, `max_depth=40`, `max_features='sqrt'`, `n_jobs=-1` | Parallel multi-threaded bagging to compress variance. |

---

## 5. Comparative Performance Results

Evaluated on 20,000 held-out unseen articles (100% natural test distribution):

| Model Architecture | Training Accuracy (%) | Testing Accuracy (%) | Macro Precision (%) | Macro Recall (%) | Macro F1-Score (%) | Overfitting Gap (%) | Target (>80%) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| Random Forest (100 Trees) | 80.91 | 70.77 | 69.84 | 65.21 | 66.94 | 10.14 | Failed |
| Decision Tree (Pruned) | 77.37 | 69.10 | 66.42 | 63.85 | 64.68 | 8.27 | Failed |
| K-Nearest Neighbors (K=5) | 61.52 | 44.06 | 52.14 | 41.80 | 43.10 | 17.46 | Failed |

---

## 6. Key Scientific Findings
1. The Failure of Single Axis-Aligned Splits in Sparse Text: A decision tree splits on a single feature at a time ($x_j \le \theta$). However, natural language semantics depend on linear combinations of tokens ($w^T x$). Approximating a diagonal hyperplane using stair-step orthogonal splits requires an exponential number of nodes, leading to premature leaf fragmentation.
2. Random Forest Variance Reduction: Random Forest improved testing accuracy by +1.67% over a single tree (69.10% to 70.77%) and increased Macro F1 by +2.26%, demonstrating the stabilizing effect of bootstrap aggregation.
3. Computational Scalability: KNN suffered from $O(N \cdot D)$ inference complexity per query, taking over 60 seconds to predict 20,000 test cases, whereas Random Forest inference took 1.8 seconds.
