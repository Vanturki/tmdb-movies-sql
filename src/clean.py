"""
Cleaning step (DuckDB).

The raw CSV is ~587 MB, so we never load it into pandas. Instead DuckDB
streams the file, applies all cleaning rules in SQL, and writes a compact
Parquet file that every downstream step reads.

The cleaning logic lives in `build_clean_query()` so it can be run against a
tiny in-memory table in the unit tests (same SQL, small data).
"""

from __future__ import annotations

from pathlib import Path

import duckdb


def _spam_regex(cfg: dict) -> str:
    """Combine the configured spam patterns into one case-insensitive regex."""
    patterns = cfg["cleaning"].get("spam_patterns", [])
    if not patterns:
        return "(?!)"  # matches nothing when no patterns are configured
    return "(" + "|".join(patterns) + ")"


def build_clean_query(cfg: dict, source: str = "raw") -> str:
    """Return the SQL SELECT that turns the raw `source` relation into clean rows.

    `source` is a table/view name whose columns are all VARCHAR (as produced by
    DuckDB's read_csv with all_varchar=true). Every column is TRY_CAST so bad
    values become NULL instead of crashing the query.
    """
    c = cfg["cleaning"]
    spam = _spam_regex(cfg).replace("'", "''")  # escape single quotes for SQL

    return f"""
    WITH typed AS (
        SELECT
            TRY_CAST(id AS BIGINT)                         AS id,
            trim(title)                                    AS title,
            trim(original_title)                           AS original_title,
            nullif(trim(status), '')                       AS status,
            TRY_CAST(release_date AS DATE)                 AS release_date,
            TRY_CAST(revenue AS DOUBLE)                    AS revenue,
            TRY_CAST(budget AS DOUBLE)                     AS budget,
            TRY_CAST(runtime AS DOUBLE)                    AS runtime,
            TRY_CAST(vote_average AS DOUBLE)               AS vote_average,
            TRY_CAST(vote_count AS BIGINT)                 AS vote_count,
            TRY_CAST(popularity AS DOUBLE)                 AS popularity,
            lower(trim(CAST(adult AS VARCHAR))) IN ('true', '1', 't') AS adult,
            nullif(trim(original_language), '')            AS original_language,
            nullif(trim(genres), '')                       AS genres,
            nullif(trim(production_countries), '')         AS production_countries,
            nullif(trim(spoken_languages), '')             AS spoken_languages,
            nullif(trim(keywords), '')                     AS keywords,
            overview
        FROM {source}
    ),
    filtered AS (
        SELECT *
        FROM typed
        WHERE id IS NOT NULL
          AND title IS NOT NULL AND title <> ''
          AND NOT regexp_matches(lower(title), '{spam}')
          AND release_date IS NOT NULL
          AND EXTRACT(year FROM release_date) BETWEEN {c['min_year']} AND {c['max_year']}
          AND (revenue IS NULL OR (revenue >= 0 AND revenue <= {c['max_revenue']}))
          AND (budget  IS NULL OR (budget  >= 0 AND budget  <= {c['max_budget']}))
          AND (runtime IS NULL OR (runtime >= 0 AND runtime <= {c['max_runtime']}))
          AND (vote_average IS NULL OR (vote_average BETWEEN 0 AND 10))
    ),
    deduped AS (
        SELECT * EXCLUDE (rn) FROM (
            SELECT *,
                   row_number() OVER (PARTITION BY id ORDER BY vote_count DESC NULLS LAST) AS rn
            FROM filtered
        )
        WHERE rn = 1
    )
    SELECT
        id,
        title,
        original_title,
        status,
        release_date,
        EXTRACT(year  FROM release_date)::INT            AS release_year,
        (EXTRACT(year FROM release_date)::INT / 10) * 10 AS release_decade,
        EXTRACT(month FROM release_date)::INT            AS release_month,
        revenue,
        budget,
        runtime,
        vote_average,
        vote_count,
        popularity,
        adult,
        coalesce(original_language, 'Unknown')           AS original_language,
        genres,
        trim(split_part(genres, ',', 1))                 AS primary_genre,
        coalesce(production_countries, 'Unknown')        AS production_countries,
        spoken_languages,
        keywords,
        overview,
        -- Financial metrics only make sense when both budget and revenue are known.
        CASE WHEN revenue > 0 AND budget > 0 THEN revenue - budget END               AS profit,
        CASE WHEN revenue > 0 AND budget > 0 THEN round(revenue / budget, 4) END      AS roi,
        CASE WHEN revenue > 0 AND budget > 0
             THEN round((revenue - budget) / budget * 100, 2) END                    AS profit_pct,
        (revenue > 0 AND budget > 0)                     AS has_financials
    FROM deduped
    """


def clean_in_connection(con: duckdb.DuckDBPyConnection, cfg: dict,
                        source: str = "raw", dest: str = "clean") -> None:
    """Run the cleaning query on `source` and materialise a `dest` table.

    Used by both the parquet writer and the unit tests.
    """
    con.execute(f"CREATE OR REPLACE TABLE {dest} AS {build_clean_query(cfg, source)}")


def _diagnostics(con: duckdb.DuckDBPyConnection, cfg: dict) -> dict:
    """Count how many raw rows each major rule would reject (for the summary)."""
    c = cfg["cleaning"]
    spam = _spam_regex(cfg).replace("'", "''")
    q = f"""
    SELECT
        count(*)                                                          AS raw_rows,
        count(*) FILTER (WHERE title IS NULL OR trim(title) = '')         AS missing_title,
        count(*) FILTER (WHERE TRY_CAST(release_date AS DATE) IS NULL)    AS bad_date,
        count(*) FILTER (WHERE regexp_matches(lower(coalesce(title,'')), '{spam}')) AS spam_title,
        count(*) FILTER (WHERE TRY_CAST(revenue AS DOUBLE) > {c['max_revenue']}) AS over_cap_revenue
    FROM raw
    """
    return con.execute(q).df().iloc[0].to_dict()


def clean_to_parquet(cfg: dict, logger=None) -> dict:
    """Stream the raw CSV, clean it, and write the cleaned Parquet file.

    Returns a summary dict (row counts + diagnostics) that also gets written to
    reports/tables/cleaning_summary.csv.
    """
    raw_csv = str(cfg["paths"]["raw_csv"])
    out_parquet = Path(cfg["paths"]["processed_parquet"])
    out_parquet.parent.mkdir(parents=True, exist_ok=True)

    if logger:
        logger.info("Cleaning raw CSV: %s", raw_csv)

    con = duckdb.connect()  # in-memory database
    try:
        # all_varchar=true keeps every column as text so our TRY_CASTs decide types.
        con.execute(
            f"""
            CREATE VIEW raw AS
            SELECT * FROM read_csv('{raw_csv}',
                                   all_varchar=true, header=true,
                                   quote='"', escape='"', ignore_errors=true)
            """
        )

        diag = _diagnostics(con, cfg)
        clean_in_connection(con, cfg, source="raw", dest="clean")
        clean_rows = con.execute("SELECT count(*) FROM clean").fetchone()[0]

        con.execute(
            f"COPY clean TO '{out_parquet.as_posix()}' (FORMAT PARQUET, COMPRESSION ZSTD)"
        )
    finally:
        con.close()

    raw_rows = int(diag["raw_rows"])
    summary = {
        "raw_rows": raw_rows,
        "clean_rows": int(clean_rows),
        "dropped_rows": raw_rows - int(clean_rows),
        "pct_kept": round(100 * int(clean_rows) / raw_rows, 2) if raw_rows else 0.0,
        "missing_title": int(diag["missing_title"]),
        "bad_or_missing_date": int(diag["bad_date"]),
        "spam_titles": int(diag["spam_title"]),
        "over_cap_revenue": int(diag["over_cap_revenue"]),
    }

    if logger:
        logger.info(
            "Cleaning done: %s raw -> %s clean rows (%.1f%% kept, %s dropped)",
            f"{summary['raw_rows']:,}", f"{summary['clean_rows']:,}",
            summary["pct_kept"], f"{summary['dropped_rows']:,}",
        )
    return summary
