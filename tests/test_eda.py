"""Tests for the EDA summary functions."""

from __future__ import annotations

from eda import (explode_genres, genre_stats, summary_kpis, top_revenue,
                 top_roi, yearly_trend)


def test_kpis(clean_df, cfg):
    k = summary_kpis(clean_df, cfg)
    assert k["total_movies"] == 4
    assert k["year_min"] == 2000 and k["year_max"] == 2010
    # Credible financials require vote_count >= 100: rows A (1500) and C (9000);
    # row D has only 80 votes and row B has no financials.
    assert k["movies_with_financials"] == 2


def test_explode_genres(clean_df):
    g = explode_genres(clean_df)
    # "Action, Thriller" + "Comedy" + "Action, Drama" + "Drama" = 6 (movie, genre) rows
    assert len(g) == 6
    assert set(g["genre"]) == {"Action", "Thriller", "Comedy", "Drama"}


def test_top_revenue_excludes_zero_financials(clean_df, cfg):
    tr = top_revenue(clean_df, cfg)
    # The row with revenue 500M must be first; the zero-financial row is excluded.
    assert tr.iloc[0]["title"] == "C"
    assert (tr["revenue"] > 0).all()


def test_top_roi_requires_real_budget(clean_df, cfg):
    roi = top_roi(clean_df, cfg)
    assert not roi.empty
    assert (roi["budget"] >= 100000).all()


def test_yearly_trend_sorted(clean_df, cfg):
    yt = yearly_trend(clean_df, cfg)
    assert list(yt["release_year"]) == sorted(yt["release_year"])


def test_genre_stats_counts(clean_df, cfg):
    gs = genre_stats(clean_df, cfg)
    action = gs[gs["genre"] == "Action"].iloc[0]
    assert action["movie_count"] == 2   # two movies tagged Action
