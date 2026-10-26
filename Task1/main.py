
import csv
import hashlib
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone, date
from pathlib import Path
from urllib.parse import urlencode, urlsplit, urlunsplit, parse_qsl

import requests
import feedparser
from bs4 import BeautifulSoup


# =========================================================
# SETTINGS
# =========================================================

BASE = Path(__file__).resolve().parent / "Output"
BASE.mkdir(parents=True, exist_ok=True)

CSV_PATH = BASE / "articles_100k_dataset.csv"
SUMMARY_PATH = BASE / "source_summary.csv"
FAILED_PATH = BASE / "failed_urls.csv"

TARGET = 100_000
WORKERS = 8
TIMEOUT = 25
RETRIES = 2
CHECKPOINT = 20

COLS = [
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

# Existing datasets to import and deduplicate.
SEED_CSV_FILES = [
    "articles_sitemap_dataset.csv",
    "latest_articles.csv",
    "articles_playwright_hybrid_dataset.csv",
    "bbc_articles.csv",
]

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/130.0 Safari/537.36"
    )
}

logging.basicConfig(
    filename=str(BASE / "news_collector_csv.log"),
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)


# =========================================================
# DIRECT RSS SOURCES
# =========================================================

SOURCES = [
    ("BBC World", "https://feeds.bbci.co.uk/news/world/rss.xml"),
    ("BBC Top Stories", "https://feeds.bbci.co.uk/news/rss.xml"),
    ("BBC Business", "https://feeds.bbci.co.uk/news/business/rss.xml"),
    ("BBC Technology", "https://feeds.bbci.co.uk/news/technology/rss.xml"),
    ("BBC Science", "https://feeds.bbci.co.uk/news/science_and_environment/rss.xml"),

    ("Guardian World", "https://www.theguardian.com/world/rss"),
    ("Guardian UK", "https://www.theguardian.com/uk/rss"),
    ("Guardian Technology", "https://www.theguardian.com/technology/rss"),
    ("Guardian Business", "https://www.theguardian.com/business/rss"),
    ("Guardian Science", "https://www.theguardian.com/science/rss"),

    ("NYT World", "https://rss.nytimes.com/services/xml/rss/nyt/World.xml"),
    ("NYT Technology", "https://rss.nytimes.com/services/xml/rss/nyt/Technology.xml"),
    ("NYT Business", "https://rss.nytimes.com/services/xml/rss/nyt/Business.xml"),
    ("NYT Science", "https://rss.nytimes.com/services/xml/rss/nyt/Science.xml"),
    ("NYT Health", "https://rss.nytimes.com/services/xml/rss/nyt/Health.xml"),

    ("NPR News", "https://feeds.npr.org/1001/rss.xml"),
    ("NPR World", "https://feeds.npr.org/1004/rss.xml"),
    ("NPR Technology", "https://feeds.npr.org/1019/rss.xml"),

    ("Sky News World", "https://feeds.skynews.com/feeds/rss/world.xml"),
    ("Sky News Technology", "https://feeds.skynews.com/feeds/rss/technology.xml"),

    ("Deutsche Welle", "https://rss.dw.com/rdf/rss-en-all"),
    ("France 24", "https://www.france24.com/en/rss"),
    ("Al Jazeera", "https://www.aljazeera.com/xml/rss/all.xml"),
    ("Euronews", "https://www.euronews.com/rss"),

    ("The Hindu", "https://www.thehindu.com/news/international/feeder/default.rss"),
    ("Indian Express", "https://indianexpress.com/section/world/feed/"),
    ("Dawn", "https://www.dawn.com/feeds/home"),
    ("Japan Times", "https://www.japantimes.co.jp/feed/"),

    ("CBC News", "https://www.cbc.ca/webfeed/rss/rss-topstories"),
    ("CBS News", "https://www.cbsnews.com/latest/rss/main"),
    ("USA Today", "https://rssfeeds.usatoday.com/usatoday-NewsTopStories"),

    ("Politico", "https://rss.politico.com/politics-news.xml"),
    ("The Hill", "https://thehill.com/feed/"),
    ("ABC News", "https://abcnews.go.com/abcnews/topstories"),

    ("TechCrunch", "https://techcrunch.com/feed/"),
    ("Ars Technica", "https://feeds.arstechnica.com/arstechnica/index"),
    ("The Verge", "https://www.theverge.com/rss/index.xml"),
    ("Wired", "https://www.wired.com/feed/rss"),
    ("Engadget", "https://www.engadget.com/rss.xml"),

    ("ScienceDaily", "https://www.sciencedaily.com/rss/all.xml"),
    ("Phys.org", "https://phys.org/rss-feed/"),
    ("Medical Xpress", "https://medicalxpress.com/rss-feed/"),

    ("Financial Times", "https://www.ft.com/rss/home/international"),
    ("CNBC", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
    ("The Register", "https://www.theregister.com/headlines.atom"),

    ("Fox News Latest", "https://moxie.foxnews.com/google-publisher/latest.xml"),
    ("Fox News Politics", "https://moxie.foxnews.com/google-publisher/politics.xml"),

    ("NBC News", "https://feeds.nbcnews.com/nbcnews/public/news"),
    ("AP via Flipboard", "https://flipboard.com/@associatedpress/top-stories-u7govdf1z.rss"),
    ("Hacker News", "https://news.ycombinator.com/rss"),
]


# =========================================================
# PUBLISHERS AND TOPICS
# =========================================================

PUBLISHERS = [
    ("BBC", "bbc.co.uk"),
    ("The Guardian", "theguardian.com"),
    ("New York Times", "nytimes.com"),
    ("NPR", "npr.org"),
    ("Sky News", "news.sky.com"),
    ("DW", "dw.com"),
    ("France 24", "france24.com"),
    ("Al Jazeera", "aljazeera.com"),
    ("CBC", "cbc.ca"),
    ("The Hindu", "thehindu.com"),
    ("Indian Express", "indianexpress.com"),
    ("Dawn", "dawn.com"),
    ("Japan Times", "japantimes.co.jp"),
    ("CBS News", "cbsnews.com"),
    ("ABC News", "abcnews.go.com"),
    ("NBC News", "nbcnews.com"),
    ("Politico", "politico.com"),
    ("The Hill", "thehill.com"),
    ("TechCrunch", "techcrunch.com"),
    ("Wired", "wired.com"),
]

TOPICS = [
    "world news",
    "politics",
    "business",
    "technology",
    "science",
    "health",
    "climate",
    "education",
    "cybersecurity",
    "economy",
]


# =========================================================
# GENERAL HELPERS
# =========================================================

def now_utc():
    return datetime.now(timezone.utc).isoformat()


def backup_file(path):
    """Create a timestamped backup of an existing file."""
    if not path.exists():
        return

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup = path.with_name(
        f"{path.stem}_backup_{stamp}{path.suffix}"
    )

    with path.open("rb") as src, backup.open("wb") as dst:
        while True:
            block = src.read(1024 * 1024)
            if not block:
                break
            dst.write(block)

    print(f"Backup created: {backup.name}")


def text_only(value):
    if not value:
        return ""

    return BeautifulSoup(
        str(value), "html.parser"
    ).get_text(" ", strip=True)


def normalize_url(url):
    """Normalize URLs so tracking parameters do not create duplicates."""
    try:
        parts = urlsplit(str(url).strip())

        if parts.scheme.lower() not in ("http", "https"):
            return ""

        if not parts.netloc:
            return ""

        ignored = {
            "utm_source",
            "utm_medium",
            "utm_campaign",
            "utm_term",
            "utm_content",
            "fbclid",
            "gclid",
            "mc_cid",
            "mc_eid",
        }

        query = [
            (key, value)
            for key, value in parse_qsl(
                parts.query, keep_blank_values=True
            )
            if key.lower() not in ignored
        ]

        return urlunsplit((
            parts.scheme.lower(),
            parts.netloc.lower(),
            parts.path.rstrip("/") or "/",
            urlencode(query, doseq=True),
            "",
        ))

    except (ValueError, TypeError):
        return ""


def first_value(row, names):
    """Read a value from different CSV column naming conventions."""
    lower_row = {
        str(key).strip().lower(): value
        for key, value in row.items()
        if key is not None
    }

    for name in names:
        value = lower_row.get(name.lower())

        if value is not None and str(value).strip():
            return str(value).strip()

    return ""


def standardize_row(raw):
    """Convert an existing CSV row to the common dataset format."""
    url = normalize_url(first_value(
        raw, ["url", "link", "article_url", "news_url"]
    ))

    title = first_value(
        raw, ["title", "headline", "article_title"]
    )

    if not url or not title:
        return None

    article_id = first_value(raw, ["article_id", "id"])

    if not article_id:
        article_id = hashlib.sha256(
            url.encode("utf-8")
        ).hexdigest()

    return {
        "article_id": article_id,
        "source": first_value(
            raw, ["source", "publisher", "website", "source_name"]
        ),
        "title": title,
        "description": first_value(
            raw, ["description", "summary", "snippet", "excerpt"]
        ),
        "author": first_value(
            raw, ["author", "authors", "byline"]
        ),
        "url": url,
        "published_at": first_value(
            raw, ["published_at", "published", "published_date",
                  "date", "pub_date"]
        ),
        "timezone": first_value(raw, ["timezone"]) or "UTC",
        "scraped_at": first_value(
            raw, ["scraped_at", "collected_at", "scrape_date"]
        ) or now_utc(),
    }


# =========================================================
# CSV SAVING AND IMPORTING
# =========================================================

def write_dataset(rows, append=True):
    """Save records to the main CSV dataset."""
    if not rows and append and CSV_PATH.exists():
        return

    mode = "a" if append and CSV_PATH.exists() else "w"
    encoding = "utf-8" if mode == "a" else "utf-8-sig"

    with CSV_PATH.open(
        mode, newline="", encoding=encoding
    ) as file:
        writer = csv.DictWriter(
            file,
            fieldnames=COLS,
            extrasaction="ignore",
        )

        if mode == "w":
            writer.writeheader()

        writer.writerows(rows)
        file.flush()


def load_existing_articles():
    """
    Import existing datasets, normalize their rows,
    and deduplicate by URL.
    """
    paths = [CSV_PATH]
    paths.extend(BASE / name for name in SEED_CSV_FILES)

    unique = {}
    seen_paths = set()

    for path in paths:
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path

        if resolved in seen_paths or not path.exists():
            continue

        seen_paths.add(resolved)

        try:
            with path.open(
                "r", newline="", encoding="utf-8-sig"
            ) as file:
                reader = csv.DictReader(file)

                for raw in reader:
                    row = standardize_row(raw)

                    if row:
                        unique.setdefault(row["url"], row)

        except (OSError, csv.Error, UnicodeError) as exc:
            logging.warning(
                "Could not read %s: %s", path.name, exc
            )
            print(f"Warning: could not import {path.name}: {exc}")

    # Back up an existing destination before rewriting it.
    if CSV_PATH.exists():
        backup_file(CSV_PATH)

    write_dataset(list(unique.values()), append=False)

    return set(unique.keys())


def export_reports(results):
    """Write source summary and failed-feed reports."""
    with SUMMARY_PATH.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "feed_name",
            "feed_url",
            "checked_at",
            "article_count",
            "status",
            "error",
        ])

        for result in sorted(
            results, key=lambda item: item["name"]
        ):
            writer.writerow([
                result["name"],
                result["url"],
                result.get("checked_at", ""),
                result["count"],
                result["status"],
                result["error"],
            ])

    with FAILED_PATH.open(
        "w", newline="", encoding="utf-8-sig"
    ) as file:
        writer = csv.writer(file)

        writer.writerow([
            "feed_name", "feed_url", "error", "status"
        ])

        for result in sorted(
            results, key=lambda item: item["name"]
        ):
            if result["status"] in ("failed", "empty"):
                writer.writerow([
                    result["name"],
                    result["url"],
                    result["error"],
                    result["status"],
                ])


# =========================================================
# GOOGLE NEWS RSS SEARCH GENERATION
# =========================================================

def google_rss(query):
    params = {
        "q": query,
        "hl": "en-US",
        "gl": "US",
        "ceid": "US:en",
    }

    return (
        "https://news.google.com/rss/search?"
        + urlencode(params)
    )


def monthly_windows(months):
    """Generate monthly date ranges, newest first."""
    today = date.today()
    first = date(today.year, today.month, 1)
    result = []

    for offset in range(months):
        index = first.year * 12 + first.month - 1 - offset
        year, month0 = divmod(index, 12)

        start = date(year, month0 + 1, 1)

        next_index = index + 1
        next_year, next_month0 = divmod(next_index, 12)
        end = date(next_year, next_month0 + 1, 1)

        result.append((
            start.isoformat(),
            end.isoformat(),
        ))

    return result


def build_feeds():
    """Build direct RSS, topic and historical search feeds."""
    feeds = []
    seen = set()

    def add(name, url):
        if url not in seen:
            seen.add(url)
            feeds.append((name, url))

    for name, url in SOURCES:
        add(name, url)

    # Current searches: publishers x topics.
    for publisher, domain in PUBLISHERS:
        for topic in TOPICS:
            add(
                f"Current | {publisher} | {topic}",
                google_rss(f"site:{domain} {topic}"),
            )

    # Topic searches across the previous 60 months.
    for topic in TOPICS:
        for start, end in monthly_windows(60):
            add(
                f"Topic history | {topic} | {start}",
                google_rss(
                    f"{topic} after:{start} before:{end}"
                ),
            )

    # Publisher searches across the previous 24 months.
    for publisher, domain in PUBLISHERS:
        for start, end in monthly_windows(24):
            add(
                f"Publisher history | {publisher} | {start}",
                google_rss(
                    f"site:{domain} after:{start} before:{end}"
                ),
            )

    return feeds


# =========================================================
# FETCH AND PARSE FEEDS
# =========================================================

def published_date(entry):
    parsed = (
        entry.get("published_parsed")
        or entry.get("updated_parsed")
    )

    if parsed:
        try:
            return datetime(
                *parsed[:6],
                tzinfo=timezone.utc,
            ).isoformat()

        except (TypeError, ValueError, OverflowError):
            pass

    return str(
        entry.get("published")
        or entry.get("updated")
        or ""
    ).strip()


def fetch_feed(feed):
    """Fetch one RSS feed with retries."""
    name, feed_url = feed
    last_error = ""

    for attempt in range(RETRIES + 1):
        try:
            response = requests.get(
                feed_url,
                headers=HEADERS,
                timeout=TIMEOUT,
            )
            response.raise_for_status()

            parsed = feedparser.parse(response.content)
            rows = []

            for entry in parsed.entries:
                title = text_only(
                    entry.get("title", "")
                ).strip()

                url = normalize_url(
                    entry.get("link", "")
                )

                if not title or not url:
                    continue

                article_id = hashlib.sha256(
                    url.encode("utf-8")
                ).hexdigest()

                rows.append({
                    "article_id": article_id,
                    "source": name,
                    "title": title,
                    "description": text_only(
                        entry.get("summary", "")
                        or entry.get("description", "")
                    ),
                    "author": text_only(
                        entry.get("author", "")
                    ),
                    "url": url,
                    "published_at": published_date(entry),
                    "timezone": "UTC",
                    "scraped_at": now_utc(),
                })

            return {
                "name": name,
                "url": feed_url,
                "rows": rows,
                "count": len(rows),
                "status": "ok" if rows else "empty",
                "error": "",
            }

        except Exception as exc:
            last_error = str(exc)

            logging.warning(
                "%s failed: %s", name, last_error
            )

            if attempt < RETRIES:
                time.sleep(attempt + 1)

    return {
        "name": name,
        "url": feed_url,
        "rows": [],
        "count": 0,
        "status": "failed",
        "error": last_error,
    }


# =========================================================
# MAIN COLLECTION
# =========================================================

def main():
    print("=" * 68)
    print("NEWS COLLECTOR - CSV ONLY (NO SQLITE)")
    print("=" * 68)

    known_urls = load_existing_articles()
    starting = len(known_urls)

    print(f"Existing unique articles loaded: {starting:,}")

    if starting >= TARGET:
        print("Target already reached.")
        return

    feeds = build_feeds()

    print(f"Direct RSS feeds: {len(SOURCES)}")
    print(f"Publisher domains: {len(PUBLISHERS)}")
    print(f"Topics: {len(TOPICS)}")
    print(f"Total distinct feeds/searches: {len(feeds):,}")
    print(f"Target: {TARGET:,}")
    print(f"Output folder: {BASE}")
    print(f"Dataset: {CSV_PATH.name}")
    print("Collection started. Keep this terminal open.")
    print("-" * 68)

    feed_results = []
    pending_rows = []
    inserted_total = 0
    completed = 0

    try:
        with ThreadPoolExecutor(
            max_workers=WORKERS
        ) as pool:

            futures = {
                pool.submit(fetch_feed, feed): feed
                for feed in feeds
            }

            for future in as_completed(futures):
                result = future.result()
                result["checked_at"] = now_utc()
                feed_results.append(result)

                for row in result["rows"]:
                    if len(known_urls) >= TARGET:
                        break

                    url = row["url"]

                    if url in known_urls:
                        continue

                    known_urls.add(url)
                    pending_rows.append(row)
                    inserted_total += 1

                completed += 1

                # Save progress after each checkpoint.
                if completed % CHECKPOINT == 0:
                    write_dataset(
                        pending_rows,
                        append=True,
                    )
                    pending_rows.clear()

                    export_reports(feed_results)

                    print(
                        f"[{completed}/{len(feeds)}] "
                        f"Unique articles: {len(known_urls):,} | "
                        f"New this run: {inserted_total:,}"
                    )

                if len(known_urls) >= TARGET:
                    print("Target reached. Saving progress.")

                    for other in futures:
                        if other is not future:
                            other.cancel()

                    break

    except KeyboardInterrupt:
        print("\nStop requested. Saving collected progress...")
        raise

    finally:
        # Save all records collected since the last checkpoint.
        write_dataset(
            pending_rows,
            append=True,
        )
        export_reports(feed_results)

    final_count = len(known_urls)

    print("\n" + "=" * 68)
    print("COLLECTION FINISHED")
    print(f"Before run: {starting:,}")
    print(f"New unique articles this run: {inserted_total:,}")
    print(f"Total unique articles: {final_count:,}")
    print(f"Dataset: {CSV_PATH}")
    print(f"Source summary: {SUMMARY_PATH}")
    print(f"Failed/empty feeds: {FAILED_PATH}")
    print("=" * 68)

    if final_count < TARGET:
        print(
            "The 100,000 target was not reached. RSS and Google "
            "News results are limited, may overlap, and do not "
            "guarantee 100,000 unique articles."
        )
    else:
        print("Target of 100,000 unique article URLs reached.")


if __name__ == "__main__":
    try:
        main()

    except KeyboardInterrupt:
        print(
            "Stopped by user. Collected progress has been saved."
        )

    except Exception as exc:
        logging.exception("Collector stopped")
        print(f"\nERROR: {exc}")
        print("Check the log file in the Output folder.")
