"""Tests for the validation gates."""

from __future__ import annotations

import numpy as np
import pytest

from validate import ValidationError, validate_clean_df


def test_clean_gate_passes_on_good_data(clean_df, cfg):
    report = validate_clean_df(clean_df, cfg)
    assert report.ok, report.summary()


def test_null_title_fails(clean_df, cfg):
    bad = clean_df.copy()
    bad.loc[0, "title"] = None
    report = validate_clean_df(bad, cfg)
    assert not report.ok
    assert any(c.name == "no_null_title" for c in report.failures())


def test_rating_out_of_range_fails(clean_df, cfg):
    bad = clean_df.copy()
    bad.loc[0, "vote_average"] = 99  # impossible rating
    report = validate_clean_df(bad, cfg)
    assert not report.ok
    assert any(c.name == "rating_in_range" for c in report.failures())


def test_duplicate_id_fails(clean_df, cfg):
    bad = clean_df.copy()
    bad.loc[1, "id"] = 1  # create a duplicate id
    report = validate_clean_df(bad, cfg)
    assert not report.ok
    assert any(c.name == "unique_id" for c in report.failures())


def test_hard_fail_raises(clean_df, cfg):
    cfg["validation"]["hard_fail"] = True
    bad = clean_df.copy()
    bad.loc[0, "title"] = None
    with pytest.raises(ValidationError):
        validate_clean_df(bad, cfg)
