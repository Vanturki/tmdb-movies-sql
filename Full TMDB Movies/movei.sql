select * from movies limit 10;

-- ============================================================
-- 1. TOP RATED MOVIES
-- ============================================================

-- Top 20 highest rated movies (min 1000 votes to filter obscure titles)
SELECT title, vote_average, vote_count, release_date
FROM movies
WHERE vote_count >= 1000
ORDER BY vote_average DESC
LIMIT 20;

-- Top 10 highest rated movies per decade
SELECT *
FROM (
    SELECT
        title,
        vote_average,
        vote_count,
        release_date,
        (EXTRACT(YEAR FROM release_date)::int / 10) * 10 AS decade,
        ROW_NUMBER() OVER (
            PARTITION BY (EXTRACT(YEAR FROM release_date)::int / 10) * 10
            ORDER BY vote_average DESC
        ) AS rank
    FROM movies
    WHERE vote_count >= 1000
      AND release_date IS NOT NULL
) ranked
WHERE rank <= 10
ORDER BY decade DESC, rank;

-- ============================================================
-- 2. REVENUE ANALYSIS
-- ============================================================

-- Top 20 highest grossing movies of all time
SELECT title, revenue, budget, release_date
FROM movies
WHERE revenue > 0
ORDER BY revenue DESC
LIMIT 20;

-- Top 20 best ROI (return on investment)
SELECT
    title,
    budget,
    revenue,
    ROUND((revenue::numeric / budget), 2) AS roi,
    release_date
FROM movies
WHERE budget > 0 AND revenue > 0
ORDER BY roi DESC
LIMIT 20;

-- Average revenue by release year (trend over time)
SELECT
    EXTRACT(YEAR FROM release_date)::int AS release_year,
    COUNT(*) AS movie_count,
    ROUND(AVG(revenue)::numeric, 0) AS avg_revenue,
    ROUND(AVG(budget)::numeric, 0) AS avg_budget
FROM movies
WHERE release_date IS NOT NULL
  AND revenue > 0
  AND budget > 0
GROUP BY release_year
ORDER BY release_year;

-- Top 10 biggest box office flops (high budget, low revenue)
SELECT
    title,
    budget,
    revenue,
    (budget - revenue) AS loss,
    release_date
FROM movies
WHERE budget > 0 AND revenue > 0 AND revenue < budget
ORDER BY loss DESC
LIMIT 10;


-- ============================================================
-- 3. GENRE ANALYSIS
-- Teaches: LIKE, ILIKE, GROUP BY, COUNT, AVG
-- ============================================================

-- Count movies per genre (genres column stores text like "Action, Comedy")
-- ILIKE = case-insensitive pattern matching, '%' = wildcard
SELECT 'Action' AS genre, COUNT(*) FROM movies WHERE genres ILIKE '%Action%'
UNION ALL
SELECT 'Comedy', COUNT(*) FROM movies WHERE genres ILIKE '%Comedy%'
UNION ALL
SELECT 'Drama', COUNT(*) FROM movies WHERE genres ILIKE '%Drama%'
UNION ALL
SELECT 'Horror', COUNT(*) FROM movies WHERE genres ILIKE '%Horror%'
UNION ALL
SELECT 'Romance', COUNT(*) FROM movies WHERE genres ILIKE '%Romance%'
UNION ALL
SELECT 'Thriller', COUNT(*) FROM movies WHERE genres ILIKE '%Thriller%'
UNION ALL
SELECT 'Science Fiction', COUNT(*) FROM movies WHERE genres ILIKE '%Science Fiction%'
UNION ALL
SELECT 'Animation', COUNT(*) FROM movies WHERE genres ILIKE '%Animation%'
UNION ALL
SELECT 'Documentary', COUNT(*) FROM movies WHERE genres ILIKE '%Documentary%'
UNION ALL
SELECT 'Adventure', COUNT(*) FROM movies WHERE genres ILIKE '%Adventure%'
ORDER BY count DESC;

-- Top 5 highest rated genres (AVG of vote_average, min 1000 movies)
-- Shows how GROUP BY + AVG work together with a HAVING filter
SELECT 'Action' AS genre, ROUND(AVG(vote_average), 2) AS avg_rating, COUNT(*) AS movie_count
FROM movies WHERE genres ILIKE '%Action%' AND vote_count >= 50
UNION ALL
SELECT 'Comedy', ROUND(AVG(vote_average), 2), COUNT(*)
FROM movies WHERE genres ILIKE '%Comedy%' AND vote_count >= 50
UNION ALL
SELECT 'Drama', ROUND(AVG(vote_average), 2), COUNT(*)
FROM movies WHERE genres ILIKE '%Drama%' AND vote_count >= 50
UNION ALL
SELECT 'Horror', ROUND(AVG(vote_average), 2), COUNT(*)
FROM movies WHERE genres ILIKE '%Horror%' AND vote_count >= 50
UNION ALL
SELECT 'Romance', ROUND(AVG(vote_average), 2), COUNT(*)
FROM movies WHERE genres ILIKE '%Romance%' AND vote_count >= 50
UNION ALL
SELECT 'Thriller', ROUND(AVG(vote_average), 2), COUNT(*)
FROM movies WHERE genres ILIKE '%Thriller%' AND vote_count >= 50
UNION ALL
SELECT 'Science Fiction', ROUND(AVG(vote_average), 2), COUNT(*)
FROM movies WHERE genres ILIKE '%Science Fiction%' AND vote_count >= 50
UNION ALL
SELECT 'Animation', ROUND(AVG(vote_average), 2), COUNT(*)
FROM movies WHERE genres ILIKE '%Animation%' AND vote_count >= 50
UNION ALL
SELECT 'Documentary', ROUND(AVG(vote_average), 2), COUNT(*)
FROM movies WHERE genres ILIKE '%Documentary%' AND vote_count >= 50
ORDER BY avg_rating DESC
LIMIT 5;

-- Most profitable genre (average revenue per genre)
SELECT 'Action' AS genre, ROUND(AVG(revenue)::numeric, 0) AS avg_revenue
FROM movies WHERE genres ILIKE '%Action%' AND revenue > 0
UNION ALL
SELECT 'Comedy', ROUND(AVG(revenue)::numeric, 0)
FROM movies WHERE genres ILIKE '%Comedy%' AND revenue > 0
UNION ALL
SELECT 'Drama', ROUND(AVG(revenue)::numeric, 0)
FROM movies WHERE genres ILIKE '%Drama%' AND revenue > 0
UNION ALL
SELECT 'Horror', ROUND(AVG(revenue)::numeric, 0)
FROM movies WHERE genres ILIKE '%Horror%' AND revenue > 0
UNION ALL
SELECT 'Animation', ROUND(AVG(revenue)::numeric, 0)
FROM movies WHERE genres ILIKE '%Animation%' AND revenue > 0
UNION ALL
SELECT 'Science Fiction', ROUND(AVG(revenue)::numeric, 0)
FROM movies WHERE genres ILIKE '%Science Fiction%' AND revenue > 0
ORDER BY avg_revenue DESC;


-- ============================================================
-- 4. LANGUAGE & COUNTRY STATS
-- Teaches: GROUP BY, HAVING, ORDER BY, COUNT
-- ============================================================

-- Top 15 languages by movie count
-- GROUP BY groups rows with same value, COUNT(*) counts each group
SELECT original_language, COUNT(*) AS movie_count
FROM movies
WHERE original_language IS NOT NULL
GROUP BY original_language
ORDER BY movie_count DESC
LIMIT 15;

-- Average rating by language (only languages with 100+ movies)
-- HAVING filters groups AFTER aggregation (WHERE filters BEFORE)
SELECT
    original_language,
    COUNT(*) AS movie_count,
    ROUND(AVG(vote_average), 2) AS avg_rating
FROM movies
WHERE vote_count >= 10
GROUP BY original_language
HAVING COUNT(*) >= 100
ORDER BY avg_rating DESC;

-- Movies per production country (top 15)
-- Same pattern: GROUP BY + COUNT + ORDER BY
SELECT
    production_countries,
    COUNT(*) AS movie_count
FROM movies
WHERE production_countries IS NOT NULL
  AND production_countries != ''
GROUP BY production_countries
ORDER BY movie_count DESC
LIMIT 15;


-- ============================================================
-- 5. RUNTIME ANALYSIS
-- Teaches: CASE WHEN, ranges, aggregation on categories
-- ============================================================

-- Categorize movies by runtime length using CASE WHEN
-- CASE WHEN is like if/else inside SQL
SELECT
    CASE
        WHEN runtime < 60 THEN 'Short (< 1hr)'
        WHEN runtime BETWEEN 60 AND 90 THEN 'Medium (1-1.5hr)'
        WHEN runtime BETWEEN 91 AND 150 THEN 'Long (1.5-2.5hr)'
        WHEN runtime > 150 THEN 'Very Long (> 2.5hr)'
    END AS runtime_category,
    COUNT(*) AS movie_count,
    ROUND(AVG(vote_average), 2) AS avg_rating
FROM movies
WHERE runtime > 0
GROUP BY runtime_category
ORDER BY movie_count DESC;

-- Average rating by runtime category (do longer movies get better ratings?)
SELECT
    CASE
        WHEN runtime BETWEEN 0 AND 60 THEN '0-60 min'
        WHEN runtime BETWEEN 61 AND 90 THEN '61-90 min'
        WHEN runtime BETWEEN 91 AND 120 THEN '91-120 min'
        WHEN runtime BETWEEN 121 AND 150 THEN '121-150 min'
        WHEN runtime BETWEEN 151 AND 180 THEN '151-180 min'
        WHEN runtime > 180 THEN '180+ min'
    END AS runtime_range,
    COUNT(*) AS movie_count,
    ROUND(AVG(vote_average), 2) AS avg_rating,
    ROUND(AVG(revenue)::numeric, 0) AS avg_revenue
FROM movies
WHERE runtime > 0 AND vote_count >= 50
GROUP BY runtime_range
ORDER BY runtime_range;

-- Top 10 longest movies (realistic: exclude data errors)
SELECT title, runtime, vote_average, release_date
FROM movies
WHERE runtime > 0 AND runtime < 1000
ORDER BY runtime DESC
LIMIT 10;

-- Top 10 shortest feature films (at least 40 min)
SELECT title, runtime, vote_average, release_date
FROM movies
WHERE runtime >= 40
ORDER BY runtime ASC
LIMIT 10;


-- ============================================================
-- 6. POPULARITY & TRENDS
-- Teaches: EXTRACT, date functions, time series analysis
-- ============================================================

-- Number of movies released per year
-- EXTRACT pulls parts (year, month, day) from a date column
SELECT
    EXTRACT(YEAR FROM release_date)::int AS release_year,
    COUNT(*) AS movie_count
FROM movies
WHERE release_date IS NOT NULL
GROUP BY release_year
ORDER BY release_year;

-- Most popular movie per year (using window function ROW_NUMBER)
SELECT *
FROM (
    SELECT
        title,
        popularity,
        EXTRACT(YEAR FROM release_date)::int AS release_year,
        ROW_NUMBER() OVER (
            PARTITION BY EXTRACT(YEAR FROM release_date)::int
            ORDER BY popularity DESC
        ) AS rank
    FROM movies
    WHERE release_date IS NOT NULL
      AND popularity IS NOT NULL
) ranked
WHERE rank = 1
ORDER BY release_year DESC
LIMIT 30;

-- Which month releases the most movies?
-- EXTRACT(MONTH FROM ...) gets the month number (1-12)
SELECT
    EXTRACT(MONTH FROM release_date)::int AS release_month,
    TO_CHAR(release_date, 'Month') AS month_name,
    COUNT(*) AS movie_count
FROM movies
WHERE release_date IS NOT NULL
GROUP BY release_month, month_name
ORDER BY movie_count DESC;


-- ============================================================
-- 7. TEXT SEARCH
-- Teaches: ILIKE, pattern matching, LENGTH, string functions
-- ============================================================

-- Search movies by keyword in title (change 'war' to any word)
-- ILIKE = case-insensitive LIKE
SELECT title, vote_average, release_date, overview
FROM movies
WHERE title ILIKE '%war%'
  AND vote_count >= 100
ORDER BY vote_average DESC
LIMIT 20;

-- Search movies by keyword in overview/description
SELECT title, vote_average, release_date
FROM movies
WHERE overview ILIKE '%artificial intelligence%'
ORDER BY vote_average DESC
LIMIT 20;

-- Movies with the longest titles
-- LENGTH() returns the number of characters in a string
SELECT title, LENGTH(title) AS title_length, release_date
FROM movies
WHERE title IS NOT NULL
ORDER BY title_length DESC
LIMIT 15;

-- Movies with the shortest titles (at least 1 character)
SELECT title, LENGTH(title) AS title_length, vote_average, release_date
FROM movies
WHERE title IS NOT NULL AND LENGTH(title) >= 1
ORDER BY title_length ASC
LIMIT 15;

-- Find movies with a specific keyword tag (keywords column)
SELECT title, keywords, vote_average, release_date
FROM movies
WHERE keywords ILIKE '%robot%'
  AND vote_count >= 50
ORDER BY vote_average DESC
LIMIT 20;


-- ============================================================
-- 8. ADVANCED ANALYTICS
-- Teaches: subqueries, CTEs, PERCENT_RANK
-- ============================================================

-- Movies above average rating (subquery in WHERE)
-- The inner SELECT calculates the average, outer SELECT uses it as filter
SELECT title, vote_average, release_date
FROM movies
WHERE vote_count >= 500
  AND vote_average > (
      SELECT AVG(vote_average)
      FROM movies
      WHERE vote_count >= 500
  )
ORDER BY vote_average DESC
LIMIT 20;

-- CTE (Common Table Expression) to find each language's top-rated movie
-- WITH creates a temporary named result set you can reference below
WITH language_top AS (
    SELECT
        title,
        original_language,
        vote_average,
        vote_count,
        ROW_NUMBER() OVER (
            PARTITION BY original_language
            ORDER BY vote_average DESC
        ) AS rank
    FROM movies
    WHERE vote_count >= 100
)
SELECT title, original_language, vote_average, vote_count
FROM language_top
WHERE rank = 1
ORDER BY vote_average DESC
LIMIT 20;

-- Percentile ranking of movies by revenue
-- PERCENT_RANK gives each row a value from 0 to 1 (0% to 100%)
SELECT
    title,
    revenue,
    ROUND(PERCENT_RANK() OVER (ORDER BY revenue)::numeric * 100, 1) AS revenue_percentile
FROM movies
WHERE revenue > 0
ORDER BY revenue DESC
LIMIT 30;
