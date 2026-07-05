"""Shared pytest fixtures. Also puts src/ on the import path."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import pytest

SRC = Path(__file__).resolve().parent.parent / "src"
sys.path.insert(0, str(SRC))

from config import load_config  # noqa: E402


@pytest.fixture
def cfg():
    """Real config, but with validation floors lowered so tiny test data passes."""
    c = load_config()
    c["validation"]["min_raw_rows"] = 1
    c["validation"]["min_clean_rows"] = 1
    return c


@pytest.fixture
def raw_columns():
    """The 24 raw CSV columns (all read as text by DuckDB)."""
    return [
        "id", "title", "vote_average", "vote_count", "status", "release_date",
        "revenue", "runtime", "adult", "backdrop_path", "budget", "homepage",
        "imdb_id", "original_language", "original_title", "overview", "popularity",
        "poster_path", "tagline", "genres", "production_companies",
        "production_countries", "spoken_languages", "keywords",
    ]


@pytest.fixture
def clean_df():
    """A small, already-cleaned DataFrame for EDA / validation tests."""
    return pd.DataFrame({
        "id": [1, 2, 3, 4],
        "title": ["A", "B", "C", "D"],
        "status": ["Released"] * 4,
        "release_date": pd.to_datetime(["2000-05-01", "2001-07-03", "2010-01-10", "2010-12-25"]),
        "release_year": [2000, 2001, 2010, 2010],
        "release_decade": [2000, 2000, 2010, 2010],
        "release_month": [5, 7, 1, 12],
        "revenue": [1_000_000.0, 0.0, 500_000_000.0, 2_000_000.0],
        "budget": [500_000.0, 0.0, 200_000_000.0, 1_000_000.0],
        "runtime": [95.0, 120.0, 150.0, 88.0],
        "vote_average": [7.5, 6.0, 8.2, 5.5],
        "vote_count": [1500, 20, 9000, 80],
        "popularity": [10.0, 2.0, 55.0, 8.0],
        "original_language": ["en", "fr", "en", "en"],
        "genres": ["Action, Thriller", "Comedy", "Action, Drama", "Drama"],
        "primary_genre": ["Action", "Comedy", "Action", "Drama"],
        "profit": [500_000.0, None, 300_000_000.0, 1_000_000.0],
        "roi": [2.0, None, 2.5, 2.0],
        "profit_pct": [100.0, None, 150.0, 100.0],
        "has_financials": [True, False, True, True],
    })
