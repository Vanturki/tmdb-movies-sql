-- ============================================================
-- 06. POPULARITY & TRENDS
-- Concepts: date parts (already extracted in cleaning), time series,
--           ROW_NUMBER for "top per group"
-- ============================================================

-- Number of movies released per year.
SELECT release_year, COUNT(*) AS movie_count
FROM movies
GROUP BY release_year
ORDER BY release_year;

-- Most popular movie per year (ROW_NUMBER picks the #1 per year).
SELECT title, popularity, release_year
FROM (
    SELECT
        title, popularity, release_year,
        ROW_NUMBER() OVER (
            PARTITION BY release_year
            ORDER BY popularity DESC
        ) AS rn
    FROM movies
    WHERE popularity IS NOT NULL
) ranked
WHERE rn = 1
ORDER BY release_year DESC
LIMIT 30;

-- Which month releases the most movies?
SELECT release_month, COUNT(*) AS movie_count
FROM movies
GROUP BY release_month
ORDER BY movie_count DESC;
