-- ============================================================
-- 02. REVENUE ANALYSIS
-- Concepts: derived columns (profit/roi are pre-computed in cleaning),
--           credibility filter (has_financials + vote_count), GROUP BY, AVG
-- Note: has_financials = TRUE means both revenue and budget are known (> 0).
--       We also require some votes so vandalised billion-dollar rows are excluded.
-- ============================================================

-- Top 20 highest grossing movies of all time (credible only).
SELECT title, revenue, budget, profit, release_year
FROM movies
WHERE has_financials AND vote_count >= 100
ORDER BY revenue DESC
LIMIT 20;

-- Top 20 best ROI (roi = revenue / budget, pre-computed). Require a real budget.
SELECT title, budget, revenue, roi, release_year
FROM movies
WHERE has_financials AND vote_count >= 100 AND budget >= 100000
ORDER BY roi DESC
LIMIT 20;

-- Average revenue and budget by release year (trend over time).
SELECT
    release_year,
    COUNT(*)                     AS movie_count,
    ROUND(AVG(revenue))          AS avg_revenue,
    ROUND(AVG(budget))           AS avg_budget
FROM movies
WHERE has_financials AND vote_count >= 100
GROUP BY release_year
ORDER BY release_year;

-- Top 10 biggest box office flops (lost the most money).
SELECT title, budget, revenue, profit, release_year
FROM movies
WHERE has_financials AND vote_count >= 100 AND profit < 0
ORDER BY profit ASC
LIMIT 10;
