"""Collect tweets for a keyword query using Twitter API v2"""
import tweepy
import sqlite3
import click
import os
from datetime import datetime


def get_db(path: str = "data/tweets.db") -> sqlite3.Connection:
    import pathlib
    pathlib.Path("data").mkdir(exist_ok=True)
    conn = sqlite3.connect(path)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tweets (
            id TEXT PRIMARY KEY,
            text TEXT,
            author_id TEXT,
            created_at TEXT,
            sentiment TEXT,
            confidence REAL
        )
    """)
    conn.commit()
    return conn


@click.command()
@click.option("--query", "-q", required=True, help="Search keyword or hashtag")
@click.option("--limit", "-l", default=100, help="Max tweets to collect")
@click.option("--db", default="data/tweets.db", help="SQLite path")
def main(query: str, limit: int, db: str):
    """Collect tweets for a given query."""
    bearer_token = os.environ.get("TWITTER_BEARER_TOKEN")
    if not bearer_token:
        raise click.ClickException("Set TWITTER_BEARER_TOKEN env var")

    client = tweepy.Client(bearer_token=bearer_token, wait_on_rate_limit=True)
    conn = get_db(db)
    inserted = 0

    paginator = tweepy.Paginator(
        client.search_recent_tweets,
        query=f"{query} -is:retweet lang:en",
        tweet_fields=["created_at", "author_id", "text"],
        max_results=min(limit, 100),
    ).flatten(limit=limit)

    for tweet in paginator:
        try:
            conn.execute(
                "INSERT OR IGNORE INTO tweets (id, text, author_id, created_at) VALUES (?,?,?,?)",
                (str(tweet.id), tweet.text, str(tweet.author_id), str(tweet.created_at))
            )
            inserted += 1
        except Exception:
            pass

    conn.commit()
    conn.close()
    click.echo(f"Collected {inserted} tweets for '{query}' → {db}")


if __name__ == "__main__":
    main()
