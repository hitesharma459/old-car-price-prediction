"""Unit tests for parsing, cleaning and feature engineering."""
import math

import pandas as pd
import pytest

from ml.preprocess import (FeatureBuilder, clean_dataset, parse_first_number, parse_int,
                           parse_price, split_brand_model)


@pytest.mark.parametrize("text,expected", [
    ("10.03 Lakh", 1_003_000), ("1.75 Crore", 17_500_000), ("80,000", 80_000), ("4.50 Lakh", 450_000)])
def test_parse_price(text, expected):
    assert parse_price(text) == pytest.approx(expected)


def test_parse_numbers():
    assert parse_int("86,226 kms") == 86226
    assert parse_int("1956 cc") == 1956
    assert parse_first_number("5 Seats") == 5
    assert parse_first_number("2nd Owner") == 2
    assert math.isnan(parse_first_number("n/a"))


@pytest.mark.parametrize("name,expected", [
    ("Maruti Swift Dzire VDI", ("Maruti", "Swift Dzire")),
    ("Maruti Alto 800 LXI", ("Maruti", "Alto 800")),
    ("Land Rover Range Rover 3.0 Petrol LWB Vogue", ("Land Rover", "Range Rover")),
    ("Mercedes-Benz C-Class C 220d", ("Mercedes-Benz", "C-Class")),
    ("BMW 5 Series 520d Luxury", ("BMW", "5 Series")),
    ("Volvo XC 90 D5", ("Volvo", "XC90")),
    ("Hyundai Creta 1.6 SX", ("Hyundai", "Creta")),
])
def test_split_brand_model(name, expected):
    assert split_brand_model(name) == expected


def _raw(n=3):
    return pd.DataFrame({
        "Unnamed: 0": range(n),
        "car_name": ["Maruti Alto 800 LXI", "Honda City i-VTEC", "Maruti Alto 800 LXI"][:n],
        "car_prices_in_rupee": ["2.5 Lakh", "5.1 Lakh", "2.5 Lakh"][:n],
        "kms_driven": ["10,000 kms", "50,000 kms", "10,000 kms"][:n],
        "fuel_type": ["Petrol"] * n, "transmission": ["Manual"] * n,
        "ownership": ["1st Owner"] * n, "manufacture": [2015, 2014, 2015][:n],
        "engine": ["796 cc", "1497 cc", "796 cc"][:n], "Seats": ["5 Seats"] * n})


def test_clean_dataset_removes_duplicates_and_parses():
    clean, report = clean_dataset(_raw())
    assert report["duplicates_removed"] == 1 and len(clean) == 2
    assert clean["price_inr"].tolist() == [250_000, 510_000]
    assert {"brand", "model", "kms_driven", "engine_cc"} <= set(clean.columns)


def test_feature_builder_groups_rare_brands_from_training_only():
    clean, _ = clean_dataset(_raw())
    clean = pd.concat([clean, clean.iloc[[0]]], ignore_index=True)  # Maruti x2, Honda x1
    fb = FeatureBuilder(min_brand_count=2).fit(clean)
    assert fb.rare_brands_ == {"Honda"}
    out = fb.transform(clean)
    assert out.loc[clean["brand"] == "Honda", "brand"].iloc[0] == "Other"
    assert set(FeatureBuilder.NUMERIC + FeatureBuilder.CATEGORICAL) <= set(out.columns)
    assert (out["age"] >= 0).all()
