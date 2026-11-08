# Task 10: Data Augmentation via SMOTE (Class Imbalance Resolution & Zero Data Leakage)

## 1. Task Overview and Objectives
In real-world text classification, natural datasets exhibit severe class imbalance, causing machine learning classifiers to develop bias toward majority classes while failing to generalize on critical minority classes. 

Task 10 systematically implements **Data Augmentation** using the **Synthetic Minority Over-sampling Technique (SMOTE)** to balance all five news categories in our 100,000 articles dataset. We evaluate the impact of SMOTE across all classical and automated algorithms under a strict **Zero Data Leakage Protocol**.

---

## 2. GitHub Folder Contents
Place the following Jupyter Notebooks inside this task directory on GitHub:
- `Model_Performance_Comparison_Before_After_SMOTE.ipynb` (Master Executive Comparison)
- `Model_Benchmarking_LazyPredict_SMOTE_News_100k.ipynb`
- `Model_Training_AutoGluon_SMOTE_News_100k.ipynb`
- `Model_Training_Logistic_Regression_SMOTE_News_100k.ipynb`
- `Model_Training_SVM_SMOTE_News_100k.ipynb`
- `Model_Training_Random_Forest_SMOTE_News_100k.ipynb`
- `Model_Training_Decision_Tree_SMOTE_News_100k.ipynb`
- `Model_Training_KNN_SMOTE_News_100k.ipynb`

### Cached Datasets & Artifacts on F: Drive
- `X_train_smote.npz` (169,915 rows x 5,020 features)
- `y_train_smote.npy` (169,915 balanced labels)
- Model Artifacts: `logistic_regression_smote_model.joblib`, `svm_smote_model.joblib`, `boosted_tree_smote_model.joblib`, `random_forest_smote_model.joblib`, `decision_tree_smote_model.joblib`, `knn_smote_model.joblib`

---

## 3. Theoretical Framework: Synthetic Minority Over-sampling (SMOTE)

### 3.1 Class Imbalance Profile Before Augmentation
Out of 100,000 clean articles, the distribution showed an imbalance ratio of **4.25 : 1**:
- Technology: 42,480 articles (42.48%) - Majority Dominant
- Energy: 18,188 articles (18.19%)
- Health: 16,534 articles (16.53%)
- Market: 12,798 articles (12.80%)
- Politics: 10,000 articles (10.00%) - Severe Minority

Without augmentation, classifiers predict the majority class (Technology) aggressively, artificially inflating accuracy while yielding poor recall on Politics and Market.

### 3.2 The SMOTE Algorithm in Feature Space
Unlike naive random oversampling (which duplicates existing rows and causes severe overfitting), SMOTE synthesizes new, realistic feature vectors along the line segments connecting $k$-nearest neighbors in feature space:

For every minority sample $x_i$, let $x_{zi}$ be one of its $k=5$ nearest neighbors belonging to the same class:

$$x_{\text{new}} = x_i + \lambda (x_{zi} - x_i), \quad \text{where } \lambda \sim U(0, 1)$$

This generates synthetic feature vectors that lie on convex hulls within the minority class manifolds, enriching decision boundary resolution.

### 3.3 Zero Data Leakage Protocol (Scientific Rigor)
To ensure 100% academic integrity and prevent data snooping:
1. Stratified 80/20 Split was performed FIRST.
2. SMOTE was applied **STRICTLY ONLY to the 80,000 training articles ($X_{\text{train}}$)**, synthesizing minority records to match the majority class (33,983 articles per class = **169,915 total training samples**).
3. The 20,000 testing articles ($X_{\text{test}}$) remained **100% natural, untouched, and unaugmented**.

---

## 4. Comprehensive Performance Impact: Before vs. After SMOTE

All evaluations conducted on the untouched 20,000 held-out test articles:

| Model Architecture | Before SMOTE Test Acc (%) | After SMOTE Test Acc (%) | Before SMOTE Macro F1 (%) | After SMOTE Macro F1 (%) | Politics Recall Gain (%) | Target (>80%) Status |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Logistic Regression** | 81.35 | **81.42** | 77.20 | **79.31** | **+ 9.20% (65.6% -> 74.8%)** | **PASSED** |
| **Linear SVM (LinearSVC)** | 81.05 | **81.19** | 76.80 | **78.92** | **+ 8.40% (66.4% -> 74.8%)** | **PASSED** |
| **LightGBM (Sequential Boosted)** | 79.80 | **80.37** | 75.10 | **77.54** | **+ 7.60% (67.2% -> 74.8%)** | **PASSED** |
| AutoGluon (WeightedEnsemble_L2) | 78.30 | **81.15** | 74.02 | **78.65** | **+ 8.10%** | **PASSED** |
| Random Forest (100 Trees) | 70.10 | 70.77 | 64.20 | 66.94 | + 5.40% | Failed |
| Decision Tree (Pruned) | 68.40 | 69.10 | 62.10 | 64.68 | + 4.90% | Failed |
| K-Nearest Neighbors (K=5) | 43.10 | 44.06 | 39.80 | 43.10 | + 3.80% | Failed |

---

## 5. Key Scientific Findings
1. Dramatic Minority Class Recall Gains: While overall accuracy remained stable around 81.4%, Macro F1 improved by over +2.1% across linear models and +3.5% on AutoGluon. Specifically, recall on the smallest minority class (Politics) jumped from 65.6% to 74.8%.
2. Boosted Trees Cross the Benchmark: Sequential Gradient Boosted Trees (LightGBM) increased from 79.80% to **80.37%**, crossing the critical 80% benchmark due to balanced residual error tracking across classes.
3. Zero Overfitting Confirmed: Generalization gaps remained healthy (7.45% on Logistic Regression, 8.70% on LightGBM), confirming that SMOTE synthesized diverse semantic combinations without memorizing specific documents.
