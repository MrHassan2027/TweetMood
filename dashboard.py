"""Streamlit dashboard for TweetMood sentiment results"""
import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

DB_PATH = "data/tweets.db"

st.set_page_config(page_title="TweetMood", layout="wide")
st.title("TweetMood — Sentiment Dashboard")

if not Path(DB_PATH).exists():
    st.error("No tweets.db found. Run collect.py and classify.py first.")
    st.stop()

conn = sqlite3.connect(DB_PATH)
df = pd.read_sql("SELECT * FROM tweets WHERE sentiment IS NOT NULL", conn)
conn.close()

if df.empty:
    st.warning("No classified tweets found. Run classify.py first.")
    st.stop()

df["created_at"] = pd.to_datetime(df["created_at"], errors="coerce")

col1, col2, col3 = st.columns(3)
col1.metric("Total Tweets", len(df))
col2.metric("Positive", len(df[df.sentiment == "positive"]))
col3.metric("Negative", len(df[df.sentiment == "negative"]))

st.subheader("Sentiment Distribution")
c1, c2 = st.columns(2)

counts = df["sentiment"].value_counts().reset_index()
counts.columns = ["sentiment", "count"]
fig_pie = px.pie(counts, names="sentiment", values="count",
                 color="sentiment",
                 color_discrete_map={"positive": "#22c55e", "negative": "#ef4444", "neutral": "#94a3b8"})
c1.plotly_chart(fig_pie, use_container_width=True)

if df["created_at"].notna().any():
    df_time = df.dropna(subset=["created_at"])
    df_time = df_time.set_index("created_at").resample("1H")["sentiment"].value_counts().unstack(fill_value=0)
    fig_line = px.line(df_time.reset_index(), x="created_at", y=df_time.columns.tolist(), title="Trend Over Time")
    c2.plotly_chart(fig_line, use_container_width=True)

st.subheader("Top Positive Tweets")
st.dataframe(df[df.sentiment == "positive"].nlargest(5, "confidence")[["text", "confidence"]], use_container_width=True)

st.subheader("Top Negative Tweets")
st.dataframe(df[df.sentiment == "negative"].nlargest(5, "confidence")[["text", "confidence"]], use_container_width=True)
