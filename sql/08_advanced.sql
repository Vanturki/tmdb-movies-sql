-- ============================================================
-- 08. ADVANCED ANALYTICS
-- Concepts: subqueries, CTEs (WITH), PERCENT_RANK
-- ============================================================

-- Movies above the overall average rating (subquery in WHERE).
SELECT title, vote_average, release_year
FROM movies
WHERE vote_count >= 500
  AND vote_average > (
      SELECT AVG(vote_average) FROM movies WHERE vote_count >= 500
  )
ORDER BY vote_average DESC
LIMIT 20;

-- CTE: each language's single top-rated movie.
WITH language_top AS (
    SELECT
        title, original_language, vote_average, vote_count,
        ROW_NUMBER() OVER (
            PARTITION BY original_language
            ORDER BY vote_average DESC
        ) AS rn
    FROM movies
    WHERE vote_count >= 100
)
SELECT title, original_language, vote_average, vote_count
FROM language_top
WHERE rn = 1
ORDER BY vote_average DESC
LIMIT 20;

-- Percentile ranking of movies by revenue (PERCENT_RANK gives 0..1).
SELECT
    title,
    revenue,
    ROUND(PERCENT_RANK() OVER (ORDER BY revenue) * 100, 1) AS revenue_percentile
FROM movies
WHERE has_financials AND vote_count >= 100
ORDER BY revenue DESC
LIMIT 30;
