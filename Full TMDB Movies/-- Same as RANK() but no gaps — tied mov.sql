-- Same as RANK() but no gaps — tied movies share the same rank and the next rank is always +1 (1, 1, 2).

 SELECT
      title,
      vote_average,
      RANK()       OVER (ORDER BY vote_average DESC) AS rnk,
      DENSE_RANK() OVER (ORDER BY vote_average DESC) AS dense_rnk
  FROM movies
  WHERE vote_count >= 500
  LIMIT 20;