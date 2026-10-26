# Task 1: News Article Scraper

## Project Overview
This project collects news article metadata from multiple news sources using RSS feeds and Google News RSS searches. The collected data is cleaned, standardized, and saved in CSV format.

## Objectives
- Collect news article metadata from multiple sources.
- Extract article titles, URLs, descriptions, authors, and publication dates.
- Normalize URLs and remove duplicate articles.
- Save the collected dataset in CSV format.
- Generate source summaries and logs for monitoring the scraping process.

## Technologies Used
- Python
- Requests
- Feedparser
- BeautifulSoup
- CSV
- ThreadPoolExecutor for concurrent processing

## Features
- Multiple news sources and topic-based RSS searches.
- URL normalization and duplicate detection.
- Retry handling for failed requests.
- Concurrent feed processing.
- Periodic saving of collected data.
- CSV-based storage without SQLite.

## Project Structure

```text
Task1/
├── README.md
├── main.py
├── requirements.txt
└── Output/
    ├── articles_100k_dataset.csv
    ├── source_summary.csv
    └── failed_urls.csv
```

## Installation

Install Python 3, then install the required libraries:

```bash
pip install -r requirements.txt
```

## How to Run

Run the scraper from the Task1 directory:

```bash
python main.py
```

The script will collect article metadata and save the results in the Output directory.

## Output Files
- `articles_100k_dataset.csv`: Collected article metadata.
- `source_summary.csv`: Summary of collection results by source.
- `failed_urls.csv`: Feed URLs that failed or returned no usable results, according to the script's reporting logic.

## Notes and Limitations
The script collects metadata available through RSS feeds; it does not necessarily extract the full text of each article. The target of 100,000 unique article URLs is a collection goal and is not guaranteed because RSS feeds and search results have limits.

## Author
Asma Yousaf

