"""
Exploratory data analysis.

Pure functions that take the cleaned DataFrame and return small summary tables.
Being pure (DataFrame in, DataFrame out) makes them easy to unit test.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# Columns actually needed for analysis (overview/keywords are dropped to save memory).
ANALYSIS_COLUMNS = [
    "id", "title", "status", "release_date", "release_year", "release_decade",
    "release_month", "revenue", "budget", "runtime", "vote_average", "vote_count",
    "popularity", "original_language", "genres", "primary_genre", "profit", "roi",
    "profit_pct", "has_financials",
]


def load_clean(parquet_path, columns=None) -> pd.DataFrame:
    """Load the cleaned Parquet, keeping only the analysis columns by default."""
    cols = columns if columns is not None else ANALYSIS_COLUMNS
    return pd.read_parquet(parquet_path, columns=cols)


def credible_financials(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Rows whose financials are trustworthy.

    TMDB is community-edited, so vandals set fake billion-dollar revenues on
    obscure titles. Those entries always have ~0 audience votes, so we require a
    minimum vote_count for any revenue/ROI analysis.
    """
    fv = cfg["analysis"]["financial_min_votes"]
    return df[df["has_financials"] & (df["vote_count"] >= fv)]


def summary_kpis(df: pd.DataFrame, cfg: dict) -> dict:
    """Headline numbers shown at the top of the report/dashboard."""
    fin = credible_financials(df, cfg)
    return {
        "total_movies": int(len(df)),
        "year_min": int(df["release_year"].min()),
        "year_max": int(df["release_year"].max()),
        "avg_rating": round(float(df["vote_average"].dropna().mean()), 2),
        "movies_with_financials": int(len(fin)),
        "total_revenue_b": round(float(fin["revenue"].sum()) / 1e9, 1),
        "median_runtime": float(df["runtime"].dropna().median()),
    }


def top_rated(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Highest rated movies with a high vote bar (excludes niche/inflated titles)."""
    n = cfg["analysis"]["top_n"]
    mv = cfg["analysis"]["top_rated_min_votes"]
    out = df[df["vote_count"] >= mv].nlargest(n, "vote_average")
    return out[["title", "vote_average", "vote_count", "release_year"]].reset_index(drop=True)


def top_revenue(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Highest grossing movies (credible financials only)."""
    n = cfg["analysis"]["top_n"]
    out = credible_financials(df, cfg).nlargest(n, "revenue")
    return out[["title", "revenue", "budget", "profit", "release_year"]].reset_index(drop=True)


def top_roi(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Best return on investment; require a real budget to avoid tiny-budget noise."""
    n = cfg["analysis"]["top_n"]
    fin = credible_financials(df, cfg)
    out = fin[fin["budget"] >= 100000].nlargest(n, "roi")
    return out[["title", "budget", "revenue", "roi", "release_year"]].reset_index(drop=True)


def explode_genres(df: pd.DataFrame) -> pd.DataFrame:
    """One row per (movie, genre) by splitting the comma-separated genres string."""
    g = df[df["genres"].notna()].copy()
    g["genre"] = g["genres"].str.split(",")
    g = g.explode("genre")
    g["genre"] = g["genre"].str.strip()
    return g[g["genre"] != ""]


def genre_stats(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Per-genre movie count and average rating (reliable ratings only)."""
    mv = cfg["analysis"]["min_vote_count"]
    g = explode_genres(df)
    counts = g.groupby("genre")["id"].size().rename("movie_count")
    # Average rating uses only movies with enough votes to be reliable.
    reliable = g[g["vote_count"] >= mv]
    ratings = reliable.groupby("genre")["vote_average"].mean().round(2).rename("avg_rating")
    out = (
        pd.concat([counts, ratings], axis=1)
        .reset_index()
        .sort_values("movie_count", ascending=False)
    )
    return out.reset_index(drop=True)


def yearly_trend(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Movies released and average revenue/budget per year (credible financials only)."""
    fin = credible_financials(df, cfg)
    counts = df.groupby("release_year").size().rename("movie_count")
    money = fin.groupby("release_year").agg(avg_revenue=("revenue", "mean"),
                                            avg_budget=("budget", "mean"))
    out = pd.concat([counts, money], axis=1).reset_index()
    return out.sort_values("release_year").reset_index(drop=True)


def runtime_buckets(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Average rating by runtime bucket (reliable ratings only)."""
    mv = cfg["analysis"]["min_vote_count"]
    sub = df[(df["runtime"] > 0) & (df["vote_count"] >= mv)].copy()
    bins = [0, 60, 90, 120, 150, 180, np.inf]
    labels = ["0-60", "61-90", "91-120", "121-150", "151-180", "180+"]
    sub["bucket"] = pd.cut(sub["runtime"], bins=bins, labels=labels, right=True)
    out = (
        sub.groupby("bucket", observed=True)
        .agg(movie_count=("id", "size"), avg_rating=("vote_average", "mean"))
        .reset_index()
    )
    out["avg_rating"] = out["avg_rating"].round(2)
    return out


def language_stats(df: pd.DataFrame, cfg: dict) -> pd.DataFrame:
    """Top languages by movie count with their average rating."""
    n = max(cfg["analysis"]["top_n"], 15)
    out = (
        df.groupby("original_language")
        .agg(movie_count=("id", "size"), avg_rating=("vote_average", "mean"))
        .reset_index()
        .sort_values("movie_count", ascending=False)
        .head(n)
    )
    out["avg_rating"] = out["avg_rating"].round(2)
    return out.reset_index(drop=True)


def monthly_releases(df: pd.DataFrame) -> pd.DataFrame:
    """Number of movies released per calendar month."""
    out = df.groupby("release_month").size().rename("movie_count").reset_index()
    return out.sort_values("release_month").reset_index(drop=True)


def run_eda(df: pd.DataFrame, cfg: dict) -> dict[str, pd.DataFrame]:
    """Compute every summary table and return them keyed by name."""
    return {
        "top_rated": top_rated(df, cfg),
        "top_revenue": top_revenue(df, cfg),
        "top_roi": top_roi(df, cfg),
        "genre_stats": genre_stats(df, cfg),
        "yearly_trend": yearly_trend(df, cfg),
        "runtime_buckets": runtime_buckets(df, cfg),
        "language_stats": language_stats(df, cfg),
        "monthly_releases": monthly_releases(df),
    }
