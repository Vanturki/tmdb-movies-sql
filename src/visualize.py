"""
Visualization step.

Turns the EDA summary tables into PNG charts saved under reports/figures/.
Uses the non-interactive 'Agg' backend so it works headless (no GUI window).
"""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")  # must be set before importing pyplot (headless PNG export)

import matplotlib.pyplot as plt
import seaborn as sns


def _apply_theme(cfg: dict) -> None:
    """Apply the theme configured under viz: (style + palette)."""
    style = cfg["viz"].get("style", "seaborn-v0_8-darkgrid")
    if style in plt.style.available:
        plt.style.use(style)
    sns.set_palette(cfg["viz"].get("palette", "viridis"))


def _save(fig, path: Path, dpi: int) -> Path:
    fig.tight_layout()
    fig.savefig(path, dpi=dpi, bbox_inches="tight")
    plt.close(fig)
    return path


def make_charts(tables: dict, cfg: dict, logger=None) -> list[Path]:
    """Create every chart and return the list of saved PNG paths."""
    _apply_theme(cfg)
    figdir = Path(cfg["paths"]["figures_dir"])
    figdir.mkdir(parents=True, exist_ok=True)
    dpi = cfg["viz"].get("dpi", 120)
    figsize = tuple(cfg["viz"].get("figsize", [10, 6]))
    saved: list[Path] = []

    # 1. Movies released per year.
    yt = tables["yearly_trend"]
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(yt["release_year"], yt["movie_count"], color="#3b528b")
    ax.set(title="Movies Released per Year", xlabel="Year", ylabel="Movie count")
    saved.append(_save(fig, figdir / "movies_per_year.png", dpi))

    # 2. Average revenue vs budget over time.
    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(yt["release_year"], yt["avg_revenue"] / 1e6, label="Avg revenue")
    ax.plot(yt["release_year"], yt["avg_budget"] / 1e6, label="Avg budget")
    ax.set(title="Average Revenue vs Budget over Time", xlabel="Year",
           ylabel="Millions USD")
    ax.legend()
    saved.append(_save(fig, figdir / "revenue_vs_budget.png", dpi))

    # 3. Top genres by movie count.
    gs = tables["genre_stats"].head(12)
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=gs, y="genre", x="movie_count", ax=ax, hue="genre", legend=False)
    ax.set(title="Top Genres by Movie Count", xlabel="Movie count", ylabel="")
    saved.append(_save(fig, figdir / "top_genres.png", dpi))

    # 4. Average rating by runtime bucket.
    rb = tables["runtime_buckets"]
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=rb, x="bucket", y="avg_rating", ax=ax, hue="bucket", legend=False)
    ax.set(title="Average Rating by Runtime (minutes)", xlabel="Runtime bucket",
           ylabel="Average rating")
    saved.append(_save(fig, figdir / "runtime_ratings.png", dpi))

    # 5. Top 10 highest grossing movies.
    tr = tables["top_revenue"].head(10)
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=tr, y="title", x=tr["revenue"] / 1e6, ax=ax, hue="title", legend=False)
    ax.set(title="Top 10 Highest Grossing Movies", xlabel="Revenue (millions USD)", ylabel="")
    saved.append(_save(fig, figdir / "top_revenue.png", dpi))

    # 6. Releases by month.
    mr = tables["monthly_releases"]
    fig, ax = plt.subplots(figsize=figsize)
    sns.barplot(data=mr, x="release_month", y="movie_count", ax=ax,
                hue="release_month", legend=False)
    ax.set(title="Movie Releases by Month", xlabel="Month", ylabel="Movie count")
    saved.append(_save(fig, figdir / "releases_by_month.png", dpi))

    if logger:
        logger.info("Saved %d charts to %s", len(saved), figdir)
    return saved
