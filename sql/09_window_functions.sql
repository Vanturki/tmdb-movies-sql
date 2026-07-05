-- ============================================================
-- 09. WINDOW FUNCTIONS (reference set)
-- Concepts: RANK vs DENSE_RANK vs ROW_NUMBER, PARTITION BY, LEAD, LAG,
--           multiple windows in one query.
--
-- NOTE: earlier standalone versions of these queries had a bug — they
-- filtered `vote_count <= 500` / `vote_average <= 500`, which is backwards
-- (it kept low-vote noise instead of well-voted movies). Fixed below to the
-- intended `vote_count >= 500`.
-- ============================================================

-- RANK vs DENSE_RANK: RANK leaves gaps after ties, DENSE_RANK does not.
SELECT
    title, vote_average, vote_count,
    RANK()       OVER (ORDER BY vote_average DESC) AS rank_with_gaps,
    DENSE_RANK() OVER (ORDER BY vote_average DESC) AS dense_rank_no_gaps
FROM movies
WHERE vote_count >= 500          -- FIXED (was: vote_count <= 500)
ORDER BY vote_average DESC
LIMIT 25;

-- Rank movies by revenue INSIDE each genre (PARTITION BY resets the rank).
SELECT title, primary_genre, revenue, genre_rank
FROM (
    SELECT
        title, primary_genre, revenue,
        RANK() OVER (PARTITION BY primary_genre ORDER BY revenue DESC) AS genre_rank
    FROM movies
    WHERE has_financials AND vote_count >= 100
) t
WHERE genre_rank <= 5
ORDER BY primary_genre, genre_rank;

-- Top row per year via ROW_NUMBER (reset the counter each year).
SELECT title, release_year, vote_average, yr_rank
FROM (
    SELECT
        title, release_year, vote_average,
        ROW_NUMBER() OVER (PARTITION BY release_year ORDER BY vote_average DESC) AS yr_rank
    FROM movies
    WHERE vote_count >= 500       -- FIXED (was: vote_count <= 500)
) t
WHERE yr_rank = 1
ORDER BY release_year DESC
LIMIT 30;

-- Top 3 rated movies per decade (DENSE_RANK inside a subquery filter).
SELECT title, release_decade, vote_average, dr
FROM (
    SELECT
        title, release_decade, vote_average,
        DENSE_RANK() OVER (PARTITION BY release_decade ORDER BY vote_average DESC) AS dr
    FROM movies
    WHERE vote_count >= 1000      -- FIXED (was: vote_average <= 500)
) t
WHERE dr <= 3
ORDER BY release_decade DESC, dr;

-- LEAD: compare each movie's revenue to the NEXT movie in the same genre.
SELECT
    title, primary_genre, revenue,
    LEAD(revenue) OVER (PARTITION BY primary_genre ORDER BY revenue DESC) AS next_revenue
FROM movies
WHERE has_financials AND vote_count >= 100
ORDER BY primary_genre, revenue DESC
LIMIT 40;

-- LAG: revenue growth vs the PREVIOUS movie (by release date) in a genre.
SELECT
    title, primary_genre, release_date, revenue,
    revenue - LAG(revenue) OVER (PARTITION BY primary_genre ORDER BY release_date) AS growth_vs_prev
FROM movies
WHERE has_financials AND vote_count >= 100
ORDER BY primary_genre, release_date
LIMIT 40;

-- Multiple windows in one query: rank by popularity per language, plus each
-- movie's popularity vs its language average.
SELECT
    title,
    original_language,
    popularity,
    DENSE_RANK() OVER (PARTITION BY original_language ORDER BY popularity DESC) AS lang_rank,
    ROUND(AVG(popularity) OVER (PARTITION BY original_language), 2)            AS lang_avg_popularity
FROM movies
WHERE vote_count >= 500
ORDER BY original_language, lang_rank
LIMIT 50;
