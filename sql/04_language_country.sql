-- ============================================================
-- 04. LANGUAGE & COUNTRY STATS
-- Concepts: GROUP BY, HAVING (filter groups AFTER aggregation), COUNT
-- ============================================================

-- Top 15 languages by movie count.
SELECT original_language, COUNT(*) AS movie_count
FROM movies
GROUP BY original_language
ORDER BY movie_count DESC
LIMIT 15;

-- Average rating by language (only languages with 100+ rated movies).
SELECT
    original_language,
    COUNT(*)                     AS movie_count,
    ROUND(AVG(vote_average), 2)  AS avg_rating
FROM movies
WHERE vote_count >= 10
GROUP BY original_language
HAVING COUNT(*) >= 100
ORDER BY avg_rating DESC;

-- Movies per production country (top 15).
SELECT production_countries, COUNT(*) AS movie_count
FROM movies
WHERE production_countries <> 'Unknown'
GROUP BY production_countries
ORDER BY movie_count DESC
LIMIT 15;
