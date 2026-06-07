-- Full summary — rank by popularity per language, show how each movie's popularity compares to its language group average.

SELECT
    title,
    original_language,
    popularity,
    DENSE_RANK() OVER (PARTITION BY original_language ORDER BY popularity DESC) AS popularity_rank,
    ROUND (AVG(popularity) OVER (PARTITION BY original_language), 2) AS avg_popularity_per_language,
    ROUND(popularity - AVG(popularity) OVER (PARTITION BY original_language), 2) AS popularity_diff_from_avg
FROM movies
WHERE original_language IS NOT NULL
AND popularity>0
ORDER BY original_language, popularity DESC
LIMIT 40;
