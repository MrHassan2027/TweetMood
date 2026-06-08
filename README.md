# TweetMood

> Sentiment analysis pipeline: collect tweets → classify with fine-tuned BERT → live dashboard

## What it does
Collects tweets on any keyword/hashtag using the Twitter API v2, classifies each tweet's sentiment (positive / negative / neutral) using a fine-tuned `distilbert-base-uncased` model, stores results in SQLite, and visualizes them in a live Streamlit dashboard with sentiment trends over time.

## Quick Start
```bash
git clone https://github.com/yourusername/TweetMood
pip install -r requirements.txt
cp .env.example .env  # add Twitter Bearer Token

python collect.py --query "#AI" --limit 500    # collect tweets
python classify.py                              # run sentiment model
streamlit run dashboard.py                     # open live dashboard
```

## Features
- Twitter API v2 streaming/search with keyword filters
- DistilBERT fine-tuned on SST-2 (pre-trained model included)
- Batch inference with progress bar
- SQLite storage: tweet text, timestamp, sentiment, confidence score
- Streamlit dashboard:
  - Sentiment donut chart
  - Timeline trend (rolling 1-hour averages)
  - Top positive / negative tweets
  - Word cloud by sentiment
- Export filtered tweets to CSV

## Tech Stack
| Tool | Why |
|------|-----|
| Python 3.11+ | Orchestration |
| `transformers` + `torch` | DistilBERT inference |
| `tweepy` | Twitter API v2 client |
| `streamlit` | Live dashboard |
| `plotly` | Charts |
| `wordcloud` | Word frequency visualization |

## Architecture
```
TweetMood/
├── collect.py       # Fetch tweets via Twitter API v2
├── classify.py      # Run DistilBERT on stored tweets
├── dashboard.py     # Streamlit dashboard
├── model/           # Fine-tuned DistilBERT weights
└── data/
    └── tweets.db    # SQLite storage
```
