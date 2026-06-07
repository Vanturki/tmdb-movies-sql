--Ranks movies by rating — tied movies share the same rank, but the next rank skips numbers (1, 1, 3).

SELECT title, vote_average,
       RANK() OVER (ORDER BY vote_average DESC) AS rank
FROM movies
WHERE vote_count >= 100
LIMIT 20;