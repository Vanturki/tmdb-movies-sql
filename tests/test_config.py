"""Tests for the config loader."""

from __future__ import annotations

from pathlib import Path

from config import load_config


def test_paths_are_absolute(cfg):
    for key in ("raw_csv", "processed_parquet", "figures_dir"):
        assert Path(cfg["paths"][key]).is_absolute()


def test_derived_year_fields(cfg):
    # max_year should be current_year + max_year_offset.
    c = cfg["cleaning"]
    assert c["max_year"] == c["current_year"] + c["max_year_offset"]


def test_required_sections_present():
    c = load_config()
    for section in ("cleaning", "validation", "analysis", "viz", "paths", "database"):
        assert section in c
