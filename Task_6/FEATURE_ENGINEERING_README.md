# ⚙️ Feature Engineering & Representation Pipeline (100,000 News Articles)

## 📌 Executive Summary
This document provides a comprehensive technical guide to the **Feature Engineering and Text Representation Pipeline** implemented for the 100,000 news articles dataset (`preprocessed_articles_100k_clean.csv`).

The complete implementation is self-contained and fully executed in the Jupyter Notebook:  
📓 **`Feature_Engineering_News_100k.ipynb`**

The core goal of this phase is to extract, encode, and scale high-signal features from tabular metadata and textual content to prepare the dataset for classification models and set up the foundation for **Transformer Embeddings (BERT / Dense Vectors)**.

---

## 🏛️ Pipeline Architecture & Engineered Features Overview

```
Raw Clean Dataset (100k Records)
         │
         ├── [1] Target Encoding ─────────► category_id (0: Energy, 1: Health, 2: Market, 3: Politics, 4: Tech)
         │
         ├── [2] Linguistic Features ─────► title_char_len, title_word_count, desc_char_len, desc_word_count,
         │                                  title_avg_word_len, desc_avg_word_len, title_uppercase_count,
         │                                  desc_lexical_diversity
         │
         ├── [3] Temporal Features ───────► published_hour, day_of_week, is_weekend, published_month
         │
         ├── [4] Categorical Features ────► One-Hot Top 8 Domains (domain_bbc, etc.) + domain_freq
         │
         ├── [5] Feature Scaling ─────────► StandardScaler (Z-Score Normalization: Mean=0, Std=1)
         │
         ├── [6] Text Representation ─────► Bag of Words & N-Grams (Comparative Baseline)
         │
         ├── [7] Transformer Primer ──────► Text Concatenation "[TITLE] ... [DESC] ..." for 768-d Dense Vectors
         │
         └── [8] Final Matrix Split ──────► Stratified 80/20 Train-Test Split (80,000 Train / 20,000 Test)
```

---

## 📋 Step-by-Step Technical Documentation & Visual Proofs

### 1. Target Variable Encoding (`LabelEncoder`)

![FE Figure 1: Target Label Encoding Distribution](figures/fe_fig1_target_encoding.png)

* **Rationale:** Multi-class classification models and loss functions (e.g. Multi-Class Cross-Entropy) require categorical ground truth labels to be represented as discrete integers rather than raw text strings.
* **Implementation:** Scikit-Learn `LabelEncoder` was fitted across all 100,000 rows.

| Encoded ID | Category Name | Article Count | Dataset Share |
| :---: | :--- | :---: | :---: |
| **0** | Energy | 18,188 | 18.19% |
| **1** | Health | 16,534 | 16.53% |
| **2** | Market | 12,797 | 12.80% |
| **3** | Politics | 10,003 | 10.00% |
| **4** | Technology | 42,478 | 42.48% |

---

### 2. Linguistic & Statistical Text Feature Extraction

![FE Figure 2: Title and Description Word Count Distributions](figures/fe_fig2_word_distributions.png)

Raw text contains strong structural signals that correlate heavily with domain categories:
* **`title_char_len` & `desc_char_len`:** Total character lengths of headline and article body.
* **`title_word_count` & `desc_word_count`:** Total whitespace-delimited tokens.
* **`title_avg_word_len` & `desc_avg_word_len`:** Ratio of characters to words. Medical (`Health`) and technical (`Technology`) articles consistently exhibit higher average word lengths due to specialized vocabulary.
* **`title_uppercase_count`:** Count of all-caps acronyms (e.g., *AI, NASA, US, GDP, WHO, IMF*). Acronym density is a powerful differentiator for Politics, Markets, and Tech.
* **`desc_lexical_diversity`:** Type-Token Ratio ($\text{TTR} = \frac{\text{Unique Words}}{\text{Total Words}}$). Measures vocabulary richness and semantic complexity.

---

### 3. Temporal Feature Extraction (Cyclical Cadence)
From the UTC string timestamp `published_at`, 4 cyclical temporal features were derived:
* **`published_hour`:** Hour of publication (0 to 23). Captures peak syndication windows.
* **`day_of_week`:** Day index (Monday = 0 ... Sunday = 6).
* **`is_weekend`:** Binary flag (1 if Saturday or Sunday, 0 if Weekday). Financial and market articles drop drastically on weekends while general interest news persists.
* **`published_month`:** Month index (1 to 12) for seasonal tracking.

---

### 4. Categorical Feature Encoding (One-Hot & Frequency)
* **One-Hot Encoding on Top 8 Domains:**
  To prevent imposing an artificial mathematical hierarchy on independent publisher sources, the 8 highest-volume domains were one-hot encoded into binary columns:
  * `domain_bbc_co_uk`
  * `domain_theguardian_com`
  * `domain_reuters_com`
  * `domain_techcrunch_com`
  * `domain_npr_org`
  * `domain_cnbc_com`
  * `domain_bloomberg_com`
  * `domain_independent_co_uk`
* **Frequency Encoding (`domain_freq`):**
  For the remaining long-tail domains (95 total), frequency encoding was applied to capture domain prevalence without causing extreme matrix sparsity.

---

### 5. Feature Scaling (StandardScaler vs MinMaxScaler)

![FE Figure 4: Feature Scaling Comparison Before vs After StandardScaler](figures/fe_fig4_feature_scaling_comparison.png)

#### Mathematical Formulations:
$$\text{StandardScaler (Z-Score):} \quad Z = \frac{X - \mu}{\sigma} \quad \implies \quad \mu = 0, \; \sigma = 1$$

$$\text{MinMaxScaler (Bounded Range):} \quad X_{norm} = \frac{X - X_{min}}{X_{max} - X_{min}} \quad \implies \quad X_{norm} \in [0, 1]$$

#### Why StandardScaler Was Selected:
* Features such as `desc_char_len` (range: 200 to 2,000) operate on an entirely different scale than `published_hour` (range: 0 to 23) or `is_weekend` (range: 0 to 1).
* Unscaled features cause gradient descent to oscillate and distance-based algorithms to over-weight large-magnitude variables.
* **Verification:** Following `StandardScaler`, all numeric columns verified with $\text{Mean} \approx 0.0000$ and $\text{Standard Deviation} \approx 1.0000$.

---

### 6. Classical NLP vs Modern Transformer Representation

| Technique | Mechanism | Major Strength | Critical Limitation |
| :--- | :--- | :--- | :--- |
| **Bag of Words (BoW)** | Word count frequency matrix (`CountVectorizer`) | Lightweight, fast | Discards all syntax and word order. |
| **N-grams** | Contiguous $n$-token sequences (e.g. Bi-grams) | Captures phrases (*\"artificial intelligence\"*) | Exponential vocabulary explosion; sparse matrices. |
| **TF-IDF** | Term Frequency $\times$ Inverse Document Frequency | Penalizes ubiquitous stopwords | **Zero semantic context.** Fails to recognize that *\"heart attack\"* and *\"cardiac arrest\"* mean the same thing. |
| **Transformer Embeddings (BERT)** | Multi-Head Self-Attention (Vaswani et al., 2017) | **Deep contextual semantics** in dense 768-d vectors | Higher compute requirements. |

> **Strategic Decision:** In accordance with modern NLP best practices and curriculum guidance, TF-IDF was bypassed for final classification in favor of **Transformer Dense Embeddings**.

---

### 7. Research Primer: Embeddings Through Transformers
* In alignment with the foundational NeurIPS 2017 paper *"Attention Is All You Need"*, the text preprocessing pipeline formats each news record into a unified demarcation sequence:
  ```python
  df['text_for_embedding'] = "[TITLE] " + df['title'] + " [DESC] " + df['description']
  ```
* **Embedding Architecture:**
  1. Subword Tokenizer (WordPiece/BPE) maps tokens to input IDs and attention masks.
  2. Multi-Head Self-Attention layers process the sequence in parallel with $O(1)$ path length.
  3. Mean Pooling layer collapses the hidden states into a single **768-dimensional dense vector per article**, capturing holistic semantic meaning.

---

### 8. Final Feature Matrix Assembly & Stratified Train/Test Split
* All engineered scaled features, one-hot domain indicators, and temporal flags were combined into feature matrix $X$:
  * **Total Engineered Tabular Features:** 20 features
  * **Stratified 80/20 Split:**
    * **Training Set ($X_{train}$):** 80,000 articles (80.0%)
    * **Test Set ($X_{test}$):** 20,000 articles (20.0%)
* **Stratification Guarantee:** Category proportions in both train and test splits match the parent distribution down to two decimal places:
  * Technology: 42.48%
  * Energy: 18.19%
  * Health: 16.53%
  * Market: 12.80%
  * Politics: 10.00%
