# Task 3: Data Preprocessing — News Articles Dataset

## Project Overview

This project focuses on cleaning, standardizing, and validating a dataset of 100,000 news articles collected during Task 1. The purpose of preprocessing is to improve data quality and prepare the dataset for further analysis and database operations.

## Objectives

- Inspect the dataset structure and data types.
- Identify missing values and duplicate records.
- Standardize date and time columns.
- Normalize timezone values.
- Clean text columns by trimming unnecessary whitespace.
- Validate required fields and data consistency.
- Export the preprocessed dataset and a summary report.

## Dataset Information

- **Dataset:** News Articles Dataset
- **Total Records:** 100,000
- **Total Columns:** 9
- **Input File:** `articles_100k_dataset.csv`

### Dataset Columns

| Column | Description |
|---|---|
| `article_id` | Unique identifier for each article |
| `source` | News source or publisher |
| `title` | Article headline |
| `description` | Short description of the article |
| `author` | Article author, when available |
| `url` | Article webpage URL |
| `published_at` | Article publication timestamp |
| `timezone` | Timezone information |
| `scraped_at` | Timestamp when the article was collected |

## Tools and Technologies

- Python
- Pandas
- Google Colab
- CSV

## Preprocessing Steps

1. **Data Loading:** Loaded the original CSV dataset into a Pandas DataFrame.
2. **Initial Inspection:** Examined the dataset dimensions, column names, data types, and sample records.
3. **Missing Value Analysis:** Identified missing values in the `author` and `description` columns.
4. **Duplicate Detection:** Checked for duplicate rows, article IDs, and URLs.
5. **Datetime Standardization:** Parsed `published_at` and `scraped_at` into standardized UTC datetime values.
6. **Timezone Standardization:** Normalized timezone labels and represented unknown timezone values as `UNKNOWN`.
7. **Text Cleaning:** Trimmed unnecessary whitespace and standardized empty text values.
8. **Data Validation:** Checked required fields, duplicate records, timestamp validity, and data consistency.
9. **Export:** Saved the preprocessed dataset and preprocessing summary report as CSV files.

## Key Results

- **100,000 records** retained in the dataset.
- **9 columns** preserved.
- No duplicate rows, article IDs, or URLs were detected.
- All publication and scraping timestamps were successfully parsed.
- No missing values were found in the required fields: `article_id`, `source`, `title`, and `url`.
- Missing author information was retained as missing because it was not available in the original data.
- Missing descriptions were also retained rather than replaced with fabricated information.
- Unknown timezone values were standardized as `UNKNOWN`.

## Output Files

| File | Description |
|---|---|
| `data_preprocessing.ipynb` | Google Colab notebook containing the preprocessing workflow |
| `preprocessed_articles_100k.csv` | Cleaned and validated news articles dataset |
| `preprocessing_summary.csv` | Summary of preprocessing and validation metrics |

## How to Use

1. Download or clone this repository.
2. Open `data_preprocessing.ipynb` in Google Colab or Jupyter Notebook.
3. Upload `articles_100k_dataset.csv` when prompted by the notebook.
4. Run the notebook cells in order.
5. Download the generated output CSV files.

## Conclusion

The preprocessing task successfully prepared the 100,000-record news articles dataset for subsequent analysis and data management. The workflow focused on data quality, consistency, and validation while preserving the original article records and handling missing information appropriately.
