# TMDB Movies — Professional Data Analysis

An end-to-end, reproducible analysis of the **TMDB movie dataset** (~1.39M movies).
It combines a Python data pipeline with a SQL analysis layer and an interactive dashboard, following a clean **Load → Clean → EDA → Visualize → Report** workflow.

> The raw data is community-edited and contains junk (spam titles, vandalised
> billion-dollar revenues on 0-vote movies). A core goal of this project is to
> **clean that noise out** so every result is trustworthy.

---

## What's inside

```
movies/
├── config/config.yaml        # every path & threshold (nothing hardcoded)
├── src/                      # the pipeline
│   ├── config.py             # config loader
│   ├── logging_setup.py      # file + console logging
│   ├── validate.py           # raw & cleaned data validation gates
│   ├── clean.py              # DuckDB cleaning: 587 MB CSV -> compact Parquet
│   ├── eda.py                # summary tables (pure functions)
│   ├── visualize.py          # matplotlib/seaborn charts (PNG)
│   ├── report.py             # self-contained HTML report
│   └── pipeline.py           # orchestrates the whole flow
├── dashboard/app.py          # interactive Streamlit dashboard
├── sql/                      # numbered, bug-fixed SQL (DuckDB or PostgreSQL)
├── tests/                    # pytest unit tests
├── docs/data_dictionary.md   # full column reference
├── reports/                  # generated charts, tables, report.html
└── data/processed/           # cleaned Parquet (gitignored)
```

## Architecture

```
 raw CSV (587 MB)
      │  validate (schema, row count)
      ▼
   CLEAN  ── DuckDB streams the file, applies rules, writes ──►  movies_cleaned.parquet
      │                                                                │
      │  validate (nulls, ranges, duplicates)                         │
      ▼                                                               ▼
   EDA (summary tables) ──► VISUALIZE (PNG charts) ──► REPORT (report.html)
      │
      └────────────────────────────────►  Streamlit dashboard (interactive)

 sql/*.sql  ── run directly on the cleaned Parquet via DuckDB, or load into PostgreSQL
```

Every step is timed and logged to `logs/pipeline.log`.

---

## Setup

```bash
# 1. Install dependencies (uv is fast; plain pip works too)
uv pip install -r requirements.txt
#    or:  python -m pip install --user -r requirements.txt

# 2. Make sure the raw dataset is here (it is gitignored):
#    Full TMDB Movies/TMDB_movie_dataset_v11.csv
```

## Run the pipeline

```bash
python src/pipeline.py            # full Load -> Clean -> EDA -> Visualize -> Report
python src/pipeline.py --skip-clean   # reuse an existing cleaned Parquet
```

Outputs: `data/processed/movies_cleaned.parquet`, PNGs in `reports/figures/`,
summary CSVs in `reports/tables/`, and `reports/report.html`.

## Explore interactively

```bash
python -m streamlit run dashboard/app.py
```

Sidebar filters (year, genre, language, min votes) update KPIs, charts and tables live.

## Run the tests

```bash
pytest -q
```

Covers the cleaning logic (spam removal, dedupe, derived columns), both
validation gates, the EDA summaries, and the config loader.

## SQL layer

The `sql/` files run against the **cleaned** data. Fastest way (no server):

```bash
duckdb
.read sql/00_schema.sql      # creates a `movies` view over the Parquet
.read sql/01_top_rated.sql   # ...then any other file
```

They also run on PostgreSQL — see `sql/00_schema.sql` for the table + load steps.

| # | File | Concepts |
|---|------|----------|
| 00 | schema | view / table setup |
| 01 | top_rated | ORDER BY, ROW_NUMBER |
| 02 | revenue | profit/roi, credibility filter, GROUP BY |
| 03 | genres | ILIKE, string_split + UNNEST, HAVING |
| 04 | language_country | GROUP BY, HAVING |
| 05 | runtime | CASE WHEN bucketing |
| 06 | popularity_trends | time series, ROW_NUMBER per group |
| 07 | text_search | ILIKE, LENGTH |
| 08 | advanced | subqueries, CTEs, PERCENT_RANK |
| 09 | window_functions | RANK / DENSE_RANK / LEAD / LAG (bug-fixed) |

---

## Data quality — the key idea

TMDB is community-edited, so vandals set fake billion-dollar revenues on obscure
titles. Those rows always have **~0 audience votes**, so the analysis requires a
minimum `vote_count` for any financial ranking. Before/after:

| | Before (raw) | After (cleaned) |
|---|---|---|
| #1 by revenue | "In the Virtual End" — $5.0B, budget $1, **0 votes** | **Avatar** — $2.92B, 29,815 votes |
| #1 by rating | niche title with ~50 votes at 9.98 | **The Godfather** — 8.71, 18,677 votes |

See `docs/data_dictionary.md` for every column and threshold.
