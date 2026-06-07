SELECT title,vote_average,
EXTRACT(YEAR FROM release_date::date)AS year,
ROW_NUMBER() OVER (PARTITION BY EXTRACT(YEAR FROM release_date::date) ORDER BY vote_average DESC) AS row_num
FROM movies
WHERE vote_count <=500
AND release_date IS NOT NULL
AND release_date >= '2000-01-01'
ORDER BY year DESC, row_num
LIMIT 30;