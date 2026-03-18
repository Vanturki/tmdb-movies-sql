SELECT status, COUNT(*) AS total
FROM movies
GROUP BY status
ORDER BY total DESC;