# Task 2: PostgreSQL Database Integration

## Project Overview

This task focuses on importing a dataset containing 100,000 news article records into a PostgreSQL database.

The dataset was generated through the news article collection workflow in Task 1. In this task, the existing CSV dataset was used as input, and the records were imported into PostgreSQL for structured storage, querying, and verification.

The project also uses a Python virtual environment and environment variables to manage dependencies and database configuration.

## Objectives

- Set up a Python virtual environment.
- Install the required Python libraries.
- Configure PostgreSQL database connectivity.
- Import 100,000 article records from a CSV dataset into PostgreSQL.
- Store records in the `public.articles` table.
- Verify the imported records using SQL queries.
- Inspect database records using Beekeeper Studio and pgAdmin.
- Keep database credentials separate from the source code.

## Technologies Used

| Technology | Purpose |
|---|---|
| Python | Runs the CSV import workflow |
| Virtual Environment (`venv`) | Isolates project dependencies |
| Pandas | Reads and processes CSV data, where used |
| Psycopg | Connects Python to PostgreSQL |
| python-dotenv | Loads database configuration from `.env` |
| PostgreSQL | Stores article records |
| Beekeeper Studio | Provides a graphical interface for database queries |
| pgAdmin | Supports PostgreSQL database administration |
| Git and GitHub | Version control and project hosting |

## Dataset

The input dataset was:

`articles_100k_dataset.csv`

The dataset contains 100,000 news article records collected through the earlier scraping workflow.

The import workflow uses the existing CSV dataset rather than collecting another 100,000 articles from scratch.

## Database Configuration

The PostgreSQL database was configured with the following details:

- **Database:** `news_articles_db`
- **Table:** `public.articles`
- **Database role:** `news_scraper_user`
- **Host:** `localhost`
- **Port:** `5432`

Database credentials are configured through environment variables and should not be hard-coded into the Python script.

## Project Setup

### 1. Create a Virtual Environment

From the project directory, create a virtual environment:

```powershell
python -m venv .venv
```

Activate it in Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

Install the required packages:

```powershell
python -m pip install pandas "psycopg[binary]" python-dotenv
```

If the project includes a `requirements.txt` file, install dependencies using:

```powershell
python -m pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a local `.env` file containing the database settings:

```dotenv
DB_HOST=localhost
DB_PORT=5432
DB_NAME=news_articles_db
DB_USER=news_scraper_user
DB_PASSWORD=your_local_database_password
```

Replace the example password with the password configured for the PostgreSQL role.

The real `.env` file must not be committed to GitHub. Use an `.env.example` file with placeholder values if configuration documentation is needed.

### 4. Import the CSV Dataset

Run the Python importer script. For example, if the script is named `import_csv_to_postgres.py`:

```powershell
python import_csv_to_postgres.py
```

The script reads the configured CSV dataset and imports its records into the PostgreSQL table.

Make sure PostgreSQL is running and the database, table, credentials, and CSV path are configured correctly before running the importer.

**Note:** Replace the example script name with the actual filename used in this task.

## SQL Verification

After importing the dataset, the following queries can be used to verify the stored records.

### Count the Records

```sql
SELECT COUNT(*)
FROM public.articles;
```

The completed local import was verified against the 100,000-record target.

### View Sample Records

```sql
SELECT *
FROM public.articles
LIMIT 10;
```

### Count Records by News Source

```sql
SELECT
    source,
    COUNT(*) AS article_count
FROM public.articles
GROUP BY source
ORDER BY article_count DESC;
```

These queries can be executed through Beekeeper Studio or pgAdmin.

## Security and Version Control

- Keep database credentials in a local `.env` file.
- Add `.env` to `.gitignore`.
- Do not commit the `.venv` directory.
- Avoid uploading large generated CSV datasets unless explicitly required.
- Keep only the files necessary to explain and reproduce the import workflow in the repository.
- Do not expose database credentials or enable unrestricted public database access.

## Task Status

### Completed

- Python virtual environment configured.
- Required dependencies installed.
- PostgreSQL database configured locally.
- CSV dataset containing 100,000 records imported into PostgreSQL.
- Article records stored in `public.articles`.
- Record count verified using SQL.
- Beekeeper Studio and pgAdmin installed for database inspection.

## Conclusion

Task 2 demonstrates how an existing CSV dataset can be imported into PostgreSQL using Python and how the stored records can be verified through SQL queries and database management tools.

This task builds on the data collection workflow completed in Task 1 and establishes a database foundation for subsequent data-related tasks.
