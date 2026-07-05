-- ============================================================
-- 03. GENRE ANALYSIS
-- The genres column is comma-separated text ("Action, Comedy"), so we
-- either match with ILIKE or split it. primary_genre (first genre) is
-- pre-computed in cleaning for quick grouping.
-- Concepts: ILIKE, GROUP BY, COUNT, AVG, string_split
-- ============================================================

-- Movie count per primary genre (fast: uses the pre-computed column).
SELECT primary_genre, COUNT(*) AS movie_count
FROM movies
WHERE primary_genre IS NOT NULL AND primary_genre <> ''
GROUP BY primary_genre
ORDER BY movie_count DESC;

-- Count + average rating per genre, splitting the full genres list.
-- DuckDB: string_split + UNNEST turns "Action, Drama" into two rows.
SELECT
    trim(genre)                  AS genre,
    COUNT(*)                     AS movie_count,
    ROUND(AVG(vote_average) FILTER (WHERE vote_count >= 50), 2) AS avg_rating
FROM movies, UNNEST(string_split(genres, ',')) AS t(genre)
WHERE genres IS NOT NULL
GROUP BY trim(genre)
HAVING COUNT(*) >= 100
ORDER BY movie_count DESC;

-- Most profitable genre (average revenue, credible financials only).
SELECT
    trim(genre)                  AS genre,
    ROUND(AVG(revenue))          AS avg_revenue
FROM movies, UNNEST(string_split(genres, ',')) AS t(genre)
WHERE genres IS NOT NULL AND has_financials AND vote_count >= 100
GROUP BY trim(genre)
HAVING COUNT(*) >= 50
ORDER BY avg_revenue DESC;
