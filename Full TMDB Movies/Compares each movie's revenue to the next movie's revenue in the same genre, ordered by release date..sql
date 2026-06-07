-- Compares each movie's revenue to the next movie's revenue in the same genre, ordered by release date.

SELECT
    title,
    genres,
    revenue,
    release_date,
    LEAD(revenue) OVER (
      PARTITION BY genres
      ORDER BY release_date::date
    ) AS next_movie_revenue
    FROM movies
    WHERE revenue>0
    AND genres IS NOT NULL
    AND genres != ''
    AND release_date IS NOT NULL
    AND release_date != ''
ORDER BY genres, release_date::date
LIMIT 30;