"""Run sentiment classification on collected tweets using DistilBERT"""
import sqlite3
import click
from transformers import pipeline
from tqdm import tqdm


LABEL_MAP = {"POSITIVE": "positive", "NEGATIVE": "negative", "LABEL_0": "negative",
             "LABEL_1": "positive", "NEUTRAL": "neutral"}


@click.command()
@click.option("--db", default="data/tweets.db")
@click.option("--batch", default=32, help="Inference batch size")
def main(db: str, batch: int):
    """Classify tweet sentiment using DistilBERT."""
    click.echo("Loading model (distilbert-base-uncased-finetuned-sst-2-english)...")
    classifier = pipeline(
        "text-classification",
        model="distilbert-base-uncased-finetuned-sst-2-english",
        truncation=True,
        max_length=512,
    )

    conn = sqlite3.connect(db)
    rows = conn.execute(
        "SELECT id, text FROM tweets WHERE sentiment IS NULL"
    ).fetchall()

    if not rows:
        click.echo("No unclassified tweets found.")
        return

    click.echo(f"Classifying {len(rows)} tweets...")
    texts = [r[1] for r in rows]
    ids   = [r[0] for r in rows]

    results = []
    for i in tqdm(range(0, len(texts), batch)):
        batch_texts = texts[i:i + batch]
        preds = classifier(batch_texts)
        results.extend(preds)

    for tweet_id, pred in zip(ids, results):
        label = LABEL_MAP.get(pred["label"], "neutral")
        score = round(pred["score"], 4)
        conn.execute(
            "UPDATE tweets SET sentiment=?, confidence=? WHERE id=?",
            (label, score, tweet_id)
        )

    conn.commit()
    conn.close()
    click.echo(f"Classified {len(rows)} tweets.")


if __name__ == "__main__":
    main()
