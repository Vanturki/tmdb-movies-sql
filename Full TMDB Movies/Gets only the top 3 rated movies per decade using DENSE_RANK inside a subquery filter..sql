-- Gets only the top 3 rated movies per decade using DENSE_RANK inside a subquery filter.
SELECT *
FROM (SELECT
        title,
        vote_average,
        EXTRACT(YEAR FROM release_date::date)::int / 10 * 10 AS decade,
        DENSE_RANK() OVER (
        PARTITION BY EXTRACT(YEAR FROM release_date::date)::int / 10 * 10
         ORDER BY vote_average DESC)
 AS dense_rnk
FROM movies
WHERE vote_average <=500
AND release_date IS NOT NULL
AND release_date != ''
) ranked
WHERE dense_rnk<=3
ORDER BY decade DESC, dense_rnk;