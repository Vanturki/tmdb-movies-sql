-- ============================================================
-- 07. TEXT SEARCH
-- Concepts: ILIKE (case-insensitive pattern match), LENGTH, string search
-- ============================================================

-- Search movies by keyword in title (change 'war' to any word).
SELECT title, vote_average, release_year, overview
FROM movies
WHERE title ILIKE '%war%' AND vote_count >= 100
ORDER BY vote_average DESC
LIMIT 20;

-- Search movies by keyword in overview/description.
SELECT title, vote_average, release_year
FROM movies
WHERE overview ILIKE '%artificial intelligence%'
ORDER BY vote_average DESC
LIMIT 20;

-- Movies with the longest titles.
SELECT title, LENGTH(title) AS title_length, release_year
FROM movies
ORDER BY title_length DESC
LIMIT 15;

-- Find movies with a specific keyword tag.
SELECT title, keywords, vote_average, release_year
FROM movies
WHERE keywords ILIKE '%robot%' AND vote_count >= 50
ORDER BY vote_average DESC
LIMIT 20;
