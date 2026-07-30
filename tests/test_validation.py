"""Tests for raw-data validation and quality reporting."""

import pandas as pd
import pytest

from aquatic_wildlife.config import EXPECTED_COLUMNS
from aquatic_wildlife.validation import (
    DataValidationError,
    build_quality_report,
    validate_raw_data,
)


def make_raw_row(**overrides):
    """Return a minimal valid record matching the source schema."""

    row = {
        "Record_ID": 1,
        "Common_Name": "Example Fish",
        "Scientific_Name": "Exemplum aquaticus",
        "Kingdom": "Animalia",
        "Phylum": "Chordata",
        "Class": "Actinopterygii",
        "Order": "Perciformes",
        "Family": "Exemplidae",
        "Genus": "Exemplum",
        "Species": "aquaticus",
        "Habitat_Type": "Marine",
        "Depth_Min_m": 0,
        "Depth_Max_m": 100,
        "Obs_Depth_m": 20.0,
        "Location": "Example Ocean",
        "Latitude": 10.0,
        "Longitude": 20.0,
        "Diet": "Omnivore",
        "IUCN_Status": "Least Concern",
        "Estimated_Age_yr": 5.0,
        "Body_Length_cm": 25.0,
        "Body_Weight_kg": 1.5,
        "Sex": "Female",
        "Water_Temp_C": 24.0,
        "Salinity_ppt": 35.0,
        "pH": 8.1,
        "Observation_Date": "2024-01-15",
        "Observation_Method": "SCUBA Diving",
        "Biome": "Ocean",
        "Fun_Fact": "Example fact",
    }
    row.update(overrides)
    return row


def test_valid_raw_data_passes():
    df = pd.DataFrame([make_raw_row()])
    validate_raw_data(df)


def test_missing_column_raises_error():
    df = pd.DataFrame([make_raw_row()]).drop(columns=["Scientific_Name"])

    with pytest.raises(DataValidationError, match="missing expected columns"):
        validate_raw_data(df)


def test_unexpected_column_raises_error():
    df = pd.DataFrame([make_raw_row(Unexpected="value")])

    with pytest.raises(
        DataValidationError,
        match="unexpected columns",
    ):
        validate_raw_data(df)


def test_duplicate_record_id_raises_error():
    df = pd.DataFrame(
        [
            make_raw_row(),
            make_raw_row(Common_Name="Second Fish"),
        ]
    )

    with pytest.raises(DataValidationError, match="duplicate values"):
        validate_raw_data(df)


def test_quality_report_detects_ambiguous_epithet():
    rows = [
        make_raw_row(
            Record_ID=1,
            Scientific_Name="Alpha gigas",
            Species="gigas",
        ),
        make_raw_row(
            Record_ID=2,
            Scientific_Name="Beta gigas",
            Species="gigas",
        ),
    ]
    df = pd.DataFrame(rows, columns=EXPECTED_COLUMNS)

    report = build_quality_report(df)

    taxonomy = report["taxonomy_checks"]
    assert taxonomy["ambiguous_species_epithet_count"] == 1
    assert taxonomy["ambiguous_species_epithets"]["gigas"] == [
        "Alpha gigas",
        "Beta gigas",
    ]
