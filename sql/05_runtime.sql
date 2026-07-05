-- ============================================================
-- 05. RUNTIME ANALYSIS
-- Concepts: CASE WHEN bucketing, aggregation on categories
-- ============================================================

-- Categorize movies by runtime length.
SELECT
    CASE
        WHEN runtime < 60             THEN 'Short (< 1hr)'
        WHEN runtime BETWEEN 60 AND 90  THEN 'Medium (1-1.5hr)'
        WHEN runtime BETWEEN 91 AND 150 THEN 'Long (1.5-2.5hr)'
        WHEN runtime > 150            THEN 'Very Long (> 2.5hr)'
    END AS runtime_category,
    COUNT(*)                     AS movie_count,
    ROUND(AVG(vote_average), 2)  AS avg_rating
FROM movies
WHERE runtime > 0
GROUP BY runtime_category
ORDER BY movie_count DESC;

-- Do longer movies get better ratings? (reliable ratings only)
SELECT
    CASE
        WHEN runtime BETWEEN 0   AND 60  THEN '0-60 min'
        WHEN runtime BETWEEN 61  AND 90  THEN '61-90 min'
        WHEN runtime BETWEEN 91  AND 120 THEN '91-120 min'
        WHEN runtime BETWEEN 121 AND 150 THEN '121-150 min'
        WHEN runtime BETWEEN 151 AND 180 THEN '151-180 min'
        WHEN runtime > 180            THEN '180+ min'
    END AS runtime_range,
    COUNT(*)                     AS movie_count,
    ROUND(AVG(vote_average), 2)  AS avg_rating
FROM movies
WHERE runtime > 0 AND vote_count >= 50
GROUP BY runtime_range
ORDER BY runtime_range;

-- Top 10 longest movies (cleaning already caps runtime at 1000 min).
SELECT title, runtime, vote_average, release_year
FROM movies
WHERE runtime > 0
ORDER BY runtime DESC
LIMIT 10;
