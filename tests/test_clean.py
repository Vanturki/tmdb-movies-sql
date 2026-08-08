"""Tests for the DuckDB cleaning logic (run against a tiny in-memory table)."""

from __future__ import annotations

import duckdb
import pytest

from clean import build_clean_query, clean_in_connection


def _make_raw(con, raw_columns, rows):
    """Create a `raw` table (all VARCHAR) and insert dict rows."""
    cols = ", ".join(f'"{c}" VARCHAR' for c in raw_columns)
    con.execute(f"CREATE TABLE raw ({cols})")
    for r in rows:
        values = [str(r.get(c)) if r.get(c) is not None else None for c in raw_columns]
        placeholders = ", ".join(["?"] * len(raw_columns))
        con.execute(f"INSERT INTO raw VALUES ({placeholders})", values)


@pytest.fixture
def con(cfg, raw_columns):
    """A DuckDB connection with a small, deliberately messy raw table."""
    c = duckdb.connect()
    rows = [
        # good row
        {"id": "1", "title": "Good Movie", "release_date": "2005-06-01",
         "revenue": "1000000", "budget": "500000", "runtime": "120",
         "vote_average": "7.5", "vote_count": "1200", "genres": "Action, Drama",
         "original_language": "en", "adult": "False"},
        # spam title -> dropped
        {"id": "2", "title": "Unsubscribe from Hulu", "release_date": "2010-01-01",
         "revenue": "0", "budget": "0", "vote_average": "1", "vote_count": "0"},
        # missing/invalid date -> dropped
        {"id": "3", "title": "No Date", "release_date": "",
         "revenue": "5000", "budget": "1000", "vote_average": "6", "vote_count": "10"},
        # over-cap revenue (junk) -> dropped
        {"id": "4", "title": "Fake Money", "release_date": "2012-03-03",
         "revenue": "4999999999999", "budget": "10", "vote_average": "5", "vote_count": "3"},
        # duplicate id (keep the higher vote_count one)
        {"id": "1", "title": "Good Movie Dupe", "release_date": "2005-06-01",
         "revenue": "1000000", "budget": "500000", "runtime": "120",
         "vote_average": "7.5", "vote_count": "50", "genres": "Action", "adult": "False"},
    ]
    _make_raw(c, raw_columns, rows)
    yield c
    c.close()


def test_query_is_valid_sql(cfg):
    assert "SELECT" in build_clean_query(cfg).upper()


def test_spam_and_bad_rows_removed(con, cfg):
    clean_in_connection(con, cfg)
    titles = [r[0] for r in con.execute("SELECT title FROM clean").fetchall()]
    assert "Unsubscribe from Hulu" not in titles   # spam removed
    assert "No Date" not in titles                 # bad date removed
    assert "Fake Money" not in titles              # over-cap revenue removed


def test_dedupe_keeps_highest_votes(con, cfg):
    clean_in_connection(con, cfg)
    rows = con.execute("SELECT id, title, vote_count FROM clean WHERE id = 1").fetchall()
    assert len(rows) == 1                            # deduped to one row
    assert rows[0][2] == 1200                        # kept the higher vote_count


def test_derived_columns(con, cfg):
    clean_in_connection(con, cfg)
    row = con.execute(
        "SELECT profit, roi, has_financials, primary_genre, release_year "
        "FROM clean WHERE id = 1"
    ).fetchone()
    profit, roi, has_fin, primary_genre, year = row
    assert profit == 500000            # revenue - budget
    assert roi == 2.0                  # revenue / budget
    assert has_fin is True
    assert primary_genre == "Action"   # first genre token
    assert year == 2005


def test_short_titles_removed(con, cfg):
    # عناوين أقل من min_title_length (بعد trim) يجب أن تُسقط، وعنوان بطول الحدّ الأدنى يبقى.
    con.execute(
        "INSERT INTO raw (id, title, release_date, revenue, budget, vote_average, vote_count) "
        "VALUES "
        "('10', 'A', '2015-01-01', '0', '0', '6', '5'),"          # حرف واحد -> يُسقط
        "('11', '   ', '2015-01-01', '0', '0', '6', '5'),"        # فراغات فقط -> يُسقط
        "('12', NULL, '2015-01-01', '0', '0', '6', '5'),"         # NULL -> يُسقط
        "('13', 'Ok', '2015-01-01', '0', '0', '6', '5')"          # حرفان (حالة الحدّ) -> يبقى
    )
    clean_in_connection(con, cfg)
    ids = {r[0] for r in con.execute("SELECT id FROM clean WHERE id IN (10, 11, 12, 13)").fetchall()}
    assert ids == {13}


def test_zero_financials_give_null_ratios(con, cfg):
    # A row with revenue=0/budget=0 should survive but have null profit/roi.
    con.execute(
        "INSERT INTO raw (id, title, release_date, revenue, budget, vote_average, vote_count) "
        "VALUES ('9', 'Zero Money', '2015-01-01', '0', '0', '6', '5')"
    )
    clean_in_connection(con, cfg)
    row = con.execute("SELECT profit, roi, has_financials FROM clean WHERE id = 9").fetchone()
    assert row[0] is None and row[1] is None and row[2] is False
