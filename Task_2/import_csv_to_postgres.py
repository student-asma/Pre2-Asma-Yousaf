
import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv

# .env file se settings load karein
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

CSV_FILE = BASE_DIR / "Output" / "articles_100k_dataset.csv"

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": int(os.getenv("DB_PORT", "5432")),
    "dbname": os.getenv("DB_NAME", "news_articles_db"),
    "user": os.getenv("DB_USER", "news_scraper_user"),
    "password": os.getenv("DB_PASSWORD"),
    "connect_timeout": 10,
}

COLUMNS = [
    "article_id",
    "source",
    "title",
    "description",
    "author",
    "url",
    "published_at",
    "timezone",
    "scraped_at",
]


def main():
    if not CSV_FILE.exists():
        raise FileNotFoundError(f"CSV file nahi mili: {CSV_FILE}")

    if not DB_CONFIG["password"]:
        raise ValueError(" .env file mein DB_PASSWORD set karein.")

    print("CSV read ho rahi hai...")
    df = pd.read_csv(CSV_FILE, dtype=str).fillna("")

    missing = set(COLUMNS) - set(df.columns)
    if missing:
        raise ValueError(f"CSV mein columns missing hain: {sorted(missing)}")

    df = df[COLUMNS]
    df = df.drop_duplicates(subset=["article_id"])
    df = df[df["article_id"].str.strip() != ""]

    print(f"CSV mein unique articles: {len(df):,}")

    create_table_sql = """
        CREATE TABLE IF NOT EXISTS public.articles (
            article_id TEXT PRIMARY KEY,
            source TEXT,
            title TEXT,
            description TEXT,
            author TEXT,
            url TEXT,
            published_at TEXT,
            timezone TEXT,
            scraped_at TEXT
        );
    """

    insert_sql = """
        INSERT INTO public.articles (
            article_id, source, title, description, author,
            url, published_at, timezone, scraped_at
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (article_id) DO NOTHING;
    """

    inserted = 0

    print("PostgreSQL se connect ho raha hai...")

    with psycopg.connect(**DB_CONFIG) as conn:
        with conn.cursor() as cur:
            cur.execute(create_table_sql)

            batch_size = 2000

            for start in range(0, len(df), batch_size):
                batch = df.iloc[start:start + batch_size]
                records = list(batch.itertuples(index=False, name=None))

                cur.executemany(insert_sql, records)
                inserted += cur.rowcount

                print(
                    f"Processed: {min(start + batch_size, len(df)):,}"
                    f"/{len(df):,}"
                )

            cur.execute("SELECT COUNT(*) FROM public.articles;")
            total = cur.fetchone()[0]

        # Context manager successful hone par transaction commit karta hai.

    print("\nImport complete!")
    print(f"Is run mein insert hue: {inserted:,}")
    print(f"Database mein total articles: {total:,}")


if __name__ == "__main__":
    main()
