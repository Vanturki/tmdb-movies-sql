--Ranks movies by revenue inside each genre partition — best revenue per genre gets rank 1.

SELECT title, genres, revenue,
       RANK() OVER (PARTITION BY genres ORDER BY revenue DESC) AS revenue_rank
FROM movies
WHERE revenue > 0
AND genres IS NOT NULL
AND genres != ''
ORDER BY genres, revenue DESC
LIMIT 20;