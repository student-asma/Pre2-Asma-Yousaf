# Task 09: Maximum Margin Classification & Automated Machine Learning (SVM, LazyPredict, AutoGluon)

## 1. Task Overview and Objectives
Task 09 advances our classification research along two pivotal directions:
1. Maximum Margin Optimization: Training a Support Vector Machine (Linear SVM) to identify the optimal separating hyperplane that maximizes the geometric margin between text categories.
2. Automated Multi-Model Screening & AutoML: Implementing **LazyPredict** for rapid default algorithm benchmarking, and **Amazon AutoGluon** for automated text embedding extraction and multi-layer stacking ensembles.

---

## 2. GitHub Folder Contents
Place the following three Jupyter Notebooks inside this task directory on GitHub:
- `Model_Training_SVM_News_100k.ipynb`
- `Model_Benchmarking_LazyPredict_News_100k.ipynb`
- `Model_Training_AutoGluon_News_100k.ipynb`

### Associated Artifacts and Model Files
- `svm_model.joblib`
- AutoGluon Artifacts Directory: `AutogluonModels/news_model/`
- Datasets: `X_train_hybrid.npz`, `X_test_hybrid.npz`, `y_train.npy`, `y_test.npy`

---

## 3. Theoretical Framework and Implementation Details

### 3.1 Linear Support Vector Machine (LinearSVC)
In high-dimensional text classification ($D=5,020$), data points are often linearly separable. A Support Vector Machine constructs a hyperplane that maximizes the separation margin:

$$\min_{w, b, \xi} \frac{1}{2} \|w\|_2^2 + C \sum_{i=1}^{N} \xi_i \quad \text{subject to } y_i (w^T x_i + b) \ge 1 - \xi_i, \quad \xi_i \ge 0$$

Where:
- Margin maximization is represented by minimizing $\frac{1}{2} \|w\|_2^2$.
- $\xi_i$ are slack variables measuring margin violations.
- $C = 1.0$ is the regularization trade-off parameter.
- Loss function: Squared Hinge Loss (`loss='squared_hinge'`, `dual=False`) optimized via Coordinate Descent.

### 3.2 LazyPredict Two-Stage Benchmarking Methodology
`LazyClassifier` screens over 25 Scikit-Learn classifiers without hyperparameter tuning:
- Challenge Encountered: `LazyClassifier` internally invokes `len(X_train)`, which raises `TypeError: sparse array length is ambiguous` on SciPy sparse matrices.
- Engineering Solution (Two-Stage Pipeline):
  - Stage 1 (Screening): Deployed dense SVD components (75 features) to shortlist top performers (LinearSVC, LogisticRegression, LGBMClassifier).
  - Stage 2 (Full-Resolution Verification): Retrained the shortlisted candidates on the complete 5,020 sparse hybrid features, validating that top algorithms cross **>80% test accuracy**.

### 3.3 Amazon AutoGluon Multi-Modal Stacking Architecture
AutoGluon eliminates manual feature engineering:
- Automated Embeddings: Ingests raw news text directly, automatically generating n-gram lexical representations and text statistics.
- Multi-Layer Stacking: Trains base models (LightGBM, CatBoost, Random Forest) and stacks their cross-validated predictions into a second-level meta-model (`WeightedEnsemble_L2`).
- Evaluation Metric: Multi-class Macro F1 (`eval_metric='f1_macro'`).

---

## 4. Experimental Results and Comparative Analysis

Evaluated on 20,000 held-out unseen test articles:

| Framework / Model | Architecture | Training Accuracy (%) | Testing Accuracy (%) | Macro Precision (%) | Macro Recall (%) | Macro F1-Score (%) | Target (>80%) |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Linear SVM** | Maximum Margin LinearSVC | **92.36** | **81.19** | **80.41** | **77.62** | **78.92** | **PASSED** |
| **LazyPredict (Stage 2)** | Top Screener: LinearSVC | **92.36** | **81.19** | **80.41** | **77.62** | **78.92** | **PASSED** |
| **LazyPredict (Stage 2)** | Top Screener: LogisticReg | **88.87** | **81.42** | **80.95** | **77.89** | **79.31** | **PASSED** |
| **AutoGluon** | WeightedEnsemble_L2 | **98.42** | **81.15** | **80.20** | **77.20** | **78.65** | **PASSED** |
| **AutoGluon** | LightGBM_BAG_L1 | **89.07** | **80.37** | **79.12** | **76.18** | **77.54** | **PASSED** |
| LazyPredict (Stage 2) | RandomForestClassifier | 80.91 | 70.77 | 69.84 | 65.21 | 66.94 | Failed |
| LazyPredict (Stage 2) | DecisionTreeClassifier | 77.37 | 69.10 | 66.42 | 63.85 | 64.68 | Failed |

---

## 5. Key Technical Takeaways
1. Margin Maximization Confirmed: Linear SVM achieved 81.19% test accuracy with 78.92% Macro F1, confirming that high-dimensional lexical spaces benefit from margin-maximizing hyperplanes.
2. AutoGluon Stacking Efficacy: AutoGluon's multi-layer `WeightedEnsemble_L2` achieved 81.15% test accuracy without requiring manual feature scaling or TF-IDF vectorizer configuration, proving the power of automated text representation learning.
3. The SVD Compression Trade-Off: Truncated SVD compression down to 75-100 dimensions limits lexical discrimination to ~67%, whereas the full 5,020 sparse representation allows linear models to cross 81%.
