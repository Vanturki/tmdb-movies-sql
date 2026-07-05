-- ============================================================
-- 01. TOP RATED MOVIES
-- Concepts: WHERE, ORDER BY, ROW_NUMBER() window function
-- ============================================================

-- Top 20 highest rated movies (min 1000 votes so obscure titles don't win).
SELECT title, vote_average, vote_count, release_year
FROM movies
WHERE vote_count >= 1000
ORDER BY vote_average DESC
LIMIT 20;

-- Top 10 highest rated movies per decade (ROW_NUMBER resets per decade).
SELECT title, vote_average, vote_count, release_decade
FROM (
    SELECT
        title, vote_average, vote_count, release_decade,
        ROW_NUMBER() OVER (
            PARTITION BY release_decade
            ORDER BY vote_average DESC
        ) AS rn
    FROM movies
    WHERE vote_count >= 1000
) ranked
WHERE rn <= 10
ORDER BY release_decade DESC, vote_average DESC;
