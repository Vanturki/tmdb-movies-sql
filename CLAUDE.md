# CLAUDE.md

Guidance for Claude Code when working in this repository.

## Project Overview

End-to-end, reproducible analysis of the TMDB movie dataset (~1.39M movies).
It is **not** a SQL-only repo anymore — it is a Python pipeline plus a SQL layer
plus an interactive dashboard, following **Load → Clean → EDA → Visualize → Report**.

The raw data is community-edited and contains junk (spam titles, vandalised
billion-dollar revenues on 0-vote movies). Cleaning that noise out is central.

## Layout

- `config/config.yaml` — every path and threshold. **Change settings here, not in code.**
- `src/` — pipeline modules: `config`, `logging_setup`, `validate`, `clean`, `eda`, `visualize`, `report`, `pipeline`.
- `dashboard/app.py` — Streamlit dashboard.
- `sql/` — numbered SQL (00–09), runnable in DuckDB (over the Parquet) or PostgreSQL.
- `tests/` — pytest suite.
- `docs/data_dictionary.md` — full column reference.
- `reports/` — generated charts/tables/report.html (committed as samples).
- `data/processed/` + `logs/` + raw CSV — gitignored.

## Key commands

```bash
python -m pip install --user -r requirements.txt   # or: uv pip install -r requirements.txt
python src/pipeline.py                # full run
python src/pipeline.py --skip-clean   # reuse cleaned parquet
python -m streamlit run dashboard/app.py
pytest -q
```

## Environment notes (Windows)

- `python` here is the Windows Store build; its site-packages are read-only, so
  install with `python -m pip install --user ...` (not `uv pip install --system`).
- `streamlit`/`pytest` scripts are not on PATH — invoke via `python -m streamlit` / `python -m pytest`.
- Scripts set `sys.stdout.reconfigure(encoding='utf-8')` and matplotlib uses the
  `Agg` backend (headless PNG export).

## How the pipeline works

1. **Validate raw** — required columns + row count on the CSV (DuckDB, no full load).
2. **Clean** — DuckDB streams the 587 MB CSV, applies the rules in
   `build_clean_query()`, writes `data/processed/movies_cleaned.parquet`.
   The cleaning SQL is reused by the unit tests against a tiny in-memory table.
3. **Validate clean** — nulls / ranges / duplicate ids on the cleaned data.
4. **EDA** — pure functions in `eda.py` produce summary tables.
5. **Visualize** — `visualize.py` saves PNG charts.
6. **Report** — `report.py` builds a self-contained `reports/report.html`.

## Data-quality conventions (defined in config)

- **Reliable rating**: averages require `vote_count >= min_vote_count` (50).
- **Credible financials**: revenue/ROI require `has_financials` and
  `vote_count >= financial_min_votes` (100) — this removes the 0-vote vandalism.
- **Top rated list**: `vote_count >= top_rated_min_votes` (1000).

## When you change things

- New threshold or path → edit `config/config.yaml`.
- New cleaning rule → edit `build_clean_query()` in `src/clean.py` **and** add a
  test in `tests/test_clean.py`.
- Keep this file and `docs/data_dictionary.md` in sync after structural changes.
