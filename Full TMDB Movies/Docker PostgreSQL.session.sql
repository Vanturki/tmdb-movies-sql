SELECT title, revenue, budget,
         (revenue - budget) AS profit
  FROM movies
  WHERE revenue > 0 AND budget > 0
  ORDER BY revenue DESC
  LIMIT 10;