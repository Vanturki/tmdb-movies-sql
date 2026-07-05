"""
Interactive Streamlit dashboard for the cleaned TMDB dataset.

Run with:
    python -m streamlit run dashboard/app.py

It reads data/processed/movies_cleaned.parquet (produced by the pipeline) and
lets you explore the data with live filters instead of a fixed report.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

# Make the src/ modules importable (config + eda helpers).
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from config import load_config          # noqa: E402
from eda import ANALYSIS_COLUMNS, credible_financials, explode_genres  # noqa: E402

st.set_page_config(page_title="TMDB Movies Dashboard", page_icon="🎬", layout="wide")


@st.cache_data(show_spinner="Loading cleaned dataset…")
def get_data():
    cfg = load_config()
    df = pd.read_parquet(cfg["paths"]["processed_parquet"], columns=ANALYSIS_COLUMNS)
    return cfg, df


cfg, df = get_data()

st.title("🎬 TMDB Movies Dashboard")
st.caption("Explore the cleaned TMDB dataset. Use the sidebar filters to slice the data.")

# ----------------------------- Sidebar filters -----------------------------
st.sidebar.header("Filters")

yr_min, yr_max = int(df["release_year"].min()), int(df["release_year"].max())
year_range = st.sidebar.slider("Release year", yr_min, yr_max, (1980, yr_max))

all_genres = sorted(explode_genres(df)["genre"].dropna().unique())
picked_genres = st.sidebar.multiselect("Genres (any of)", all_genres, default=[])

top_langs = df["original_language"].value_counts().head(20).index.tolist()
picked_langs = st.sidebar.multiselect("Languages", top_langs, default=[])

min_votes = st.sidebar.number_input("Minimum vote count", min_value=0, value=100, step=50)

# ----------------------------- Apply filters -------------------------------
mask = df["release_year"].between(*year_range) & (df["vote_count"] >= min_votes)
if picked_genres:
    mask &= df["genres"].fillna("").apply(
        lambda g: any(pg in g for pg in picked_genres))
if picked_langs:
    mask &= df["original_language"].isin(picked_langs)

fdf = df[mask]

# ----------------------------- KPI row -------------------------------------
fin = credible_financials(fdf, cfg)
c1, c2, c3, c4 = st.columns(4)
c1.metric("Movies", f"{len(fdf):,}")
c2.metric("Avg rating", f"{fdf['vote_average'].mean():.2f}" if len(fdf) else "–")
c3.metric("Median runtime", f"{fdf['runtime'].median():.0f} min" if len(fdf) else "–")
c4.metric("Total revenue", f"${fin['revenue'].sum()/1e9:.1f}B" if len(fin) else "–")

if fdf.empty:
    st.warning("No movies match these filters. Loosen them in the sidebar.")
    st.stop()

# ----------------------------- Charts --------------------------------------
left, right = st.columns(2)

with left:
    st.subheader("Movies released per year")
    per_year = fdf.groupby("release_year").size().reset_index(name="count")
    st.plotly_chart(px.line(per_year, x="release_year", y="count"),
                    use_container_width=True)

    st.subheader("Rating distribution")
    st.plotly_chart(px.histogram(fdf, x="vote_average", nbins=40),
                    use_container_width=True)

with right:
    st.subheader("Top genres")
    g = explode_genres(fdf)["genre"].value_counts().head(12).reset_index()
    g.columns = ["genre", "count"]
    st.plotly_chart(px.bar(g, x="count", y="genre", orientation="h")
                    .update_yaxes(autorange="reversed"), use_container_width=True)

    st.subheader("Revenue vs budget over time")
    if len(fin):
        money = fin.groupby("release_year").agg(
            avg_revenue=("revenue", "mean"), avg_budget=("budget", "mean")).reset_index()
        st.plotly_chart(
            px.line(money, x="release_year", y=["avg_revenue", "avg_budget"]),
            use_container_width=True)
    else:
        st.info("No credible financial data in this selection.")

# ----------------------------- Tables --------------------------------------
st.subheader("🏆 Top rated (in selection)")
top_rated = fdf.nlargest(15, "vote_average")[
    ["title", "vote_average", "vote_count", "release_year", "primary_genre"]]
st.dataframe(top_rated, use_container_width=True, hide_index=True)

st.subheader("💰 Top grossing (credible financials)")
if len(fin):
    top_rev = fin.nlargest(15, "revenue")[
        ["title", "revenue", "budget", "profit", "release_year"]]
    st.dataframe(top_rev, use_container_width=True, hide_index=True)
else:
    st.info("No credible financial data in this selection.")
