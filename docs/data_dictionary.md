# Data Dictionary

Two layers of data:

1. **Raw** — `TMDB_movie_dataset_v11.csv` (24 columns, ~1.39M rows, community-edited so it contains junk).
2. **Cleaned** — `data/processed/movies_cleaned.parquet` produced by the pipeline (~1.09M rows), with typed columns, junk removed, and derived metrics added.

---

## Raw columns (`TMDB_movie_dataset_v11.csv`)

| Column | Type | Description | Quality notes |
|---|---|---|---|
| `id` | int | TMDB movie id | Unique key; a few duplicates exist |
| `title` | text | Display title | Some rows are spam (URLs, "Unsubscribe…", phone numbers) |
| `vote_average` | float | Mean user rating (0–10) | Inflated to ~10 on low-vote titles |
| `vote_count` | int | Number of user votes | **Key credibility signal** — junk/vandalised rows have ~0 votes |
| `status` | text | Released / Post Production / Rumored… | |
| `release_date` | date | Release date | Many blank or invalid; some far-future placeholders |
| `revenue` | int | Worldwide gross (USD) | 0 = unknown; vandalised rows show fake billions |
| `runtime` | int | Minutes | 0 = unknown; some absurd values (data errors) |
| `adult` | bool | Adult content flag | |
| `backdrop_path` | text | Image path | Not used in analysis |
| `budget` | int | Production budget (USD) | 0 = unknown |
| `homepage` | text | Official site URL | Not used |
| `imdb_id` | text | IMDb id | Not used |
| `original_language` | text | ISO language code | |
| `original_title` | text | Title in original language | |
| `overview` | text | Plot summary | Free text; searched with ILIKE |
| `popularity` | float | TMDB popularity score | Time-varying, not comparable across years |
| `poster_path` | text | Image path | Not used |
| `tagline` | text | Marketing tagline | Not used |
| `genres` | text | Comma-separated genres ("Action, Comedy") | **Not an array** — split on commas |
| `production_companies` | text | Comma-separated | Not used in core analysis |
| `production_countries` | text | Comma-separated | |
| `spoken_languages` | text | Comma-separated | |
| `keywords` | text | Comma-separated tags | Searched with ILIKE |

---

## Cleaned columns (`movies_cleaned.parquet`)

Includes the typed raw columns above **plus** the derived columns below. Rows are kept only if they pass the cleaning gate (valid title/date, in-range financials/runtime/rating, deduped by id).

| Column | Type | Description |
|---|---|---|
| `release_year` | int | Year extracted from `release_date` |
| `release_decade` | int | Decade bucket (e.g. 1990, 2000) |
| `release_month` | int | Month number (1–12) |
| `primary_genre` | text | First genre in the `genres` list — for quick grouping |
| `profit` | float | `revenue - budget`, only when both are known (else NULL) |
| `roi` | float | `revenue / budget`, only when both are known (else NULL) |
| `profit_pct` | float | `(revenue - budget) / budget * 100` (else NULL) |
| `has_financials` | bool | TRUE when both `revenue > 0` and `budget > 0` |

### Analysis conventions

- **Reliable rating** — averages use `vote_count >= min_vote_count` (default 50) so a single 10/10 vote can't skew a genre.
- **Credible financials** — revenue/ROI rankings require `has_financials` **and** `vote_count >= financial_min_votes` (default 100). This is what removes vandalised billion-dollar rows, which always have ~0 votes.
- **Top rated list** — uses a higher bar, `vote_count >= top_rated_min_votes` (default 1000).

All thresholds live in `config/config.yaml`.
