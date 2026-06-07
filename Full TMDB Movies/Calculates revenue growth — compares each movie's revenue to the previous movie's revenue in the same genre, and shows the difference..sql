SELECT
    title,
    genres,
    revenue,
    release_date,
    LAG(revenue) OVER (PARTITION BY genres ORDER BY release_date::date) AS prev_revenue,
    revenue - LAG(revenue) OVER (PARTITION BY genres ORDER BY release_date::date) AS revenue_growth
    FROM movies
    WHERE revenue>0
    AND genres IS NOT NULL
    AND genres != ''
    AND release_date IS NOT NULL
    AND release_date != ''
ORDER BY genres, release_date::date
LIMIT 30;