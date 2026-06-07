-- Uses PARTITION BY with multiple window functions in one query — each movie gets its rank, genre average, and its revenue compared to the genre's best.

SELECT
    title,
    genres,
    revenue,
    budget,
    DENSE_RANK() OVER (PARTITION BY genres ORDER BY revenue DESC) AS revenue_rank_in_genres,
    ROUND(AVG(revenue) OVER (PARTITION BY genres))AS avg_revenue_in_genres,
    revenue - LAG(revenue) OVER (PARTITION BY genres ORDER BY revenue DESC) AS gap_from_above
FROM movies
WHERE revenue>0
AND budget>0
AND genres IS NOT NULL
AND genres != ''
ORDER BY genres, revenue_rank_in_genres
LIMIT 30;