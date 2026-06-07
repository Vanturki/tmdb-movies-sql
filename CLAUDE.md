# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

SQL analysis project on the TMDB movie dataset using PostgreSQL. No application code — this is a data analysis repo with SQL query files and CSV exports.

## Database Setup

Start PostgreSQL via Docker:

```bash
docker run --name movies-db \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres
```

Connect using VS Code SQLTools extension (config already in `.vscode/settings.json`):

- Host: `localhost`, Port: `5432`
- User: `postgres`, Password: `postgres`, Database: `postgres`

## Importing the Dataset

After starting the container, import the CSV into the `movies` table using `\COPY` in psql:

```sql
\COPY movies FROM 'Full TMDB Movies/TMDB_movie_dataset_v11.csv' CSV HEADER;
```

Or via Docker:

```bash
docker cp "Full TMDB Movies/TMDB_movie_dataset_v11.csv" movies-db:/tmp/movies.csv
docker exec -it movies-db psql -U postgres -c "\COPY movies FROM '/tmp/movies.csv' CSV HEADER;"
```

## Files

- `Full TMDB Movies/movei.sql` — main SQL analysis file with 8 sections
- `Full TMDB Movies/TMDB_movie_dataset_v11.csv` — raw dataset (~1M rows, imported into the `movies` table)
- `Full TMDB Movies/Docker PostgreSQL.session.sql` — scratch queries run via SQLTools
- CSV exports: `Highest revenue movies.csv`, `Most popular movies.csv`, `Movie status distribution.csv`, `Movies with the biggest profit margin.csv`, `10 افلام.csv`

## Dataset Table: `movies`

Key columns: `title`, `genres`, `release_date`, `budget`, `revenue`, `vote_average`, `vote_count`, `popularity`, `runtime`, `original_language`, `production_countries`, `keywords`, `overview`

**Important:** `genres`, `production_countries`, and `keywords` are plain text fields (comma-separated strings like `"Action, Comedy"`), not arrays. Use `ILIKE '%genre%'` for filtering, not array operators.

## SQL Analysis Structure

`movei.sql` is organized into 8 sections:

| # | Section | Key SQL Concepts |
|---|---------|-----------------|
| 1 | Top Rated Movies | `ORDER BY`, `WHERE`, `ROW_NUMBER()` window function |
| 2 | Revenue Analysis | `ROI`, `AVG`, `GROUP BY`, box office flops |
| 3 | Genre Analysis | `ILIKE`, `UNION ALL`, `COUNT`, `AVG` |
| 4 | Language & Country Stats | `GROUP BY`, `HAVING` |
| 5 | Runtime Analysis | `CASE WHEN`, range bucketing |
| 6 | Popularity & Trends | `EXTRACT`, date functions, time series |
| 7 | Text Search | `ILIKE`, `LENGTH`, pattern matching |
| 8 | Advanced Analytics | CTEs (`WITH`), `PERCENT_RANK()`, subqueries |

## Important Note

After major changes, please update this file (CLAUDE.md) to keep it in sync with the project's status.
