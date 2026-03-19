# TMDB Movies SQL Analysis

A SQL analysis project using the TMDB movie dataset. The goal is to explore movie data and practice SQL queries — from basic filtering to advanced analytics.

## Dataset

- **Source:** TMDB Movie Dataset v11
- **File:** `Full TMDB Movies/TMDB_movie_dataset_v11.csv`
- **Columns:** title, genres, release_date, budget, revenue, vote_average, vote_count, popularity, runtime, original_language, production_countries, keywords, overview

## Tools

- **Database:** PostgreSQL (via Docker)
- **Editor:** VS Code + SQLTools extension
- **Environment:** WSL (Windows Subsystem for Linux)

## Setup

### 1. Start PostgreSQL with Docker

```bash
docker run --name movies-db \
  -e POSTGRES_PASSWORD=postgres \
  -p 5432:5432 \
  -d postgres
```

### 2. Connect in VS Code

Use the SQLTools extension and connect with:
- Host: `localhost`
- Port: `5432`
- User: `postgres`
- Password: `postgres`
- Database: `postgres`

### 3. Run the queries

Open `Full TMDB Movies/movei.sql` in VS Code and run any section.

## Analysis Sections

| # | Section | SQL Concepts |
|---|---------|-------------|
| 1 | Top Rated Movies | `ORDER BY`, `WHERE`, Window Functions |
| 2 | Revenue Analysis | `ROI`, `AVG`, `GROUP BY` |
| 3 | Genre Analysis | `ILIKE`, `UNION ALL`, `COUNT` |
| 4 | Language & Country Stats | `GROUP BY`, `HAVING` |
| 5 | Runtime Analysis | `CASE WHEN`, ranges |
| 6 | Popularity & Trends | `EXTRACT`, date functions |
| 7 | Text Search | `ILIKE`, `LENGTH`, pattern matching |
| 8 | Advanced Analytics | CTEs, `PERCENT_RANK`, subqueries |

## Key SQL Concepts Used

- `GROUP BY` + `HAVING` — group and filter aggregated data
- `CASE WHEN` — conditional logic inside queries
- `ROW_NUMBER()` — rank rows within groups
- `PERCENT_RANK()` — percentile ranking
- `WITH` (CTE) — reusable temporary result sets
- `EXTRACT` — pull year/month from date columns
- `ILIKE` — case-insensitive text search
