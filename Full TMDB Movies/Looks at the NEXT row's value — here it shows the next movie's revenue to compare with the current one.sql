-- Looks at the NEXT row's value — here it shows the next movie's revenue to compare with the current one.

SELECT
  title,
  release_date,
  revenue,
  LEAD (revenue) OVER (ORDER BY release_date) AS next_revenue
FROM movies
WHERE revenue>0
LIMIT 10;