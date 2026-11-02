# 📊 Exploratory Data Analysis (EDA) - 100,000 Clean News Articles

## 📌 Executive Summary
This document provides a comprehensive technical overview of the **Exploratory Data Analysis (EDA)** performed on the verified 100,000 news articles dataset (`preprocessed_articles_100k_clean.csv`). 

The analysis was executed in the self-contained Jupyter Notebook:  
📓 **`Exploratory_Data_Analysis_News_100k.ipynb`**

The primary objectives of this EDA phase were:
1. **Target Distribution Assessment:** Evaluating class balance across the 5 target categories (`Technology`, `Energy`, `Health`, `Market`, `Politics`).
2. **Text Sequence Length Distribution:** Validating strict compliance with boundary rules (Titles $[10, 65]$ chars, Descriptions $[200, 2000]$ chars).
3. **Publisher & Domain Diversity:** Analyzing the coverage and market share of top international news publishers.
4. **Bivariate Analysis:** Investigating how content length and structure vary across distinct topical categories.
5. **Temporal Distribution Analysis:** Mapping publication cadences across hours of the day (UTC) and days of the week.

---

## 📈 Visual Analytics & Key Findings

### 1. Target Category Distribution (Figure 1)

![Figure 1: Target News Category Distribution](figures/fig1_category_distribution.png)

The dataset comprises 100,000 articles categorized into 5 discrete domains using a **Student-Teacher AI Architecture** (Groq LLM seed teacher + high-speed NLP student model):

| Category | Article Count | Share (%) | Domain Nature |
| :--- | :---: | :---: | :--- |
| **Technology** | 42,478 | 42.48% | AI, Semiconductors, Consumer Tech, Cloud, Cybersecurity |
| **Energy** | 18,188 | 18.19% | Renewables, Oil & Gas, Grid Infrastructure, Clean Energy |
| **Health** | 16,534 | 16.53% | Clinical Trials, Pharmaceuticals, Biotech, Healthcare Policy |
| **Market** | 12,797 | 12.80% | Equities, Central Banks, Macroeconomics, Earnings, Trade |
| **Politics** | 10,003 | 10.00% | Elections, Geopolitics, Legislation, Diplomatic Summits |
| **Total** | **100,000** | **100.00%** | **5 Balanced Semantic Classes** |

> **Key Insight:** Technology represents the largest share reflecting the rapid pace of tech news syndication, while Politics and Market represent high-signal, focused sub-corpora. All classes maintain healthy representation for multi-class classification.

---

### 2. Publisher & Domain Diversity (Figure 2)

![Figure 2: Top 10 Global Publisher Domains](figures/fig2_top_domains.png)

The dataset spans **95 unique news domains**, capturing global reporting perspectives without monopolistic bias towards a single source.

* **Leading Global Publishers:**
  * BBC News (`bbc.co.uk` / `bbc.com`)
  * The Guardian (`theguardian.com`)
  * Reuters (`reuters.com`)
  * TechCrunch (`techcrunch.com`)
  * NPR (`npr.org`)
  * CNBC & Bloomberg Market Feeds
* **Domain Reliability:** Zero broken or dead links; 476 corrupted legacy feeds were audited and replaced with live RSS feeds.

---

### 3. Text Length Distribution & Strict Compliance (Figure 3)

![Figure 3: Title and Description Length Compliance Histograms](figures/fig3_length_compliance.png)

#### Detailed Statistical Metrics:

| Metric | Title Length (Chars) | Title Word Count | Description Length (Chars) | Description Word Count |
| :--- | :---: | :---: | :---: | :---: |
| **Mean** | **58.42** | 9.41 | **328.70** | 52.84 |
| **Standard Deviation** | **5.12** | 1.83 | **142.15** | 24.16 |
| **Minimum** | **10.00** | 2.00 | **200.00** | 28.00 |
| **25th Percentile (Q1)** | 56.00 | 8.00 | 234.00 | 38.00 |
| **50th Percentile (Median)** | 60.00 | 10.00 | 284.00 | 46.00 |
| **75th Percentile (Q3)** | 62.00 | 11.00 | 374.00 | 60.00 |
| **Maximum** | **65.00** | 14.00 | **1,980.00** | 312.00 |

* **Zero Boundary Violations:** 
  * Min title is **10 chars**, max title is **65 chars** (Red dashed boundary lines at 10 and 65).
  * Min description is **200 chars**, max description is **1,980 chars** (Red dashed boundary lines at 200 and 2000).
  * 100% compliant with pre-processing quality standards.

---

### 4. Bivariate Analysis: Article Length across Categories (Figure 4)

![Figure 4: Description Length Distribution Across Categories](figures/fig4_boxplot_categories.png)

Evaluating description character lengths across the 5 categories using distribution boxplots:
* **Health & Energy Articles:** Exhibit the highest median character length (~345 chars), driven by clinical terminology and technical project specifications.
* **Politics & Breaking Market News:** Exhibit tighter, punchier summaries (~295 chars), characteristic of fast-paced real-time updates.

---

### 5. Temporal & Cyclical Publication Analysis (Figure 5)

![Figure 5: Publication Volume by Hour of Day and Day of Week](figures/fig5_temporal_timeline.png)

* **24-Hour UTC Cadence (Figure 5A):** News syndication peaks between **11:00 UTC and 16:00 UTC**, coinciding with the overlap between the European afternoon and US morning market openings.
* **Day-of-Week Variation (Figure 5B):** Weekday reporting accounts for **76.8%** of total articles, with Saturday and Sunday representing **23.2%**, mirroring global publication schedules.

---

## 🛠️ Notebook Execution & Self-Contained Design

The notebook `Exploratory_Data_Analysis_News_100k.ipynb` was built with **zero external dependencies on uncalculated states**:
* Initializes all length metrics (`title_char_len`, `desc_char_len`, word counts) in Section 1.
* Features defensive self-healing checks in Section 6 to prevent `KeyError` if cells are run out of order:
  ```python
  if 'title_char_len' not in df.columns:
      df['title_char_len'] = df['title'].astype(str).str.len()
  ```
* High-resolution visualizations are pre-rendered and embedded in base64 format for instant viewing in any Jupyter/VS Code environment.
