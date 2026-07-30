"""Tests for cleaning, feature engineering, and taxon summaries."""

import pandas as pd

from aquatic_wildlife.data import (
    build_species_reference,
    prepare_dataset,
)
from tests.test_validation import make_raw_row


def test_prepare_dataset_adds_expected_features():
    raw = pd.DataFrame([make_raw_row()])
    processed = prepare_dataset(raw)

    expected = {
        "Taxon_ID",
        "Observation_Year",
        "Observation_Month",
        "Observation_Quarter",
        "IUCN_Risk_Score",
        "Is_Threatened",
        "Conservation_Group",
        "Depth_Range_m",
        "Relative_Depth_Position",
        "Depth_Band",
        "Body_Length_Band",
        "Latitude_Zone",
        "Hemisphere",
    }

    assert expected.issubset(processed.columns)
    assert processed.loc[0, "Taxon_ID"] == "Exemplum aquaticus"
    assert processed.loc[0, "Observation_Year"] == 2024
    assert processed.loc[0, "Depth_Range_m"] == 100
    assert processed.loc[0, "Relative_Depth_Position"] == 0.2
    assert not bool(processed.loc[0, "Is_Threatened"])


def test_threatened_classification():
    raw = pd.DataFrame(
        [
            make_raw_row(
                IUCN_Status="Endangered",
            )
        ]
    )

    processed = prepare_dataset(raw)

    assert bool(processed.loc[0, "Is_Threatened"])
    assert processed.loc[0, "Conservation_Group"] == "Threatened"
    assert processed.loc[0, "IUCN_Risk_Score"] == 5


def test_species_reference_uses_full_scientific_name():
    raw = pd.DataFrame(
        [
            make_raw_row(
                Record_ID=1,
                Common_Name="Alpha",
                Scientific_Name="Alpha gigas",
                Genus="Alpha",
                Species="gigas",
            ),
            make_raw_row(
                Record_ID=2,
                Common_Name="Beta",
                Scientific_Name="Beta gigas",
                Genus="Beta",
                Species="gigas",
            ),
        ]
    )

    processed = prepare_dataset(raw)
    reference = build_species_reference(processed)

    assert len(reference) == 2
    assert set(reference["Scientific_Name"]) == {
        "Alpha gigas",
        "Beta gigas",
    }
