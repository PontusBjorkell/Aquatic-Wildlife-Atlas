"""Data loading, cleaning, feature engineering, and reference exports."""

from __future__ import annotations

import numpy as np
import pandas as pd

from aquatic_wildlife.config import (
    BODY_LENGTH_BINS,
    BODY_LENGTH_LABELS,
    DEPTH_BINS,
    DEPTH_LABELS,
    IUCN_RISK_SCORES,
    NUMERIC_COLUMNS,
    RAW_DATA_PATH,
    TEXT_COLUMNS,
    THREATENED_STATUSES,
)
from aquatic_wildlife.validation import validate_raw_data


def load_raw_data(path=RAW_DATA_PATH) -> pd.DataFrame:
    """Load the source CSV and perform blocking structural validation."""

    if not path.exists():
        raise FileNotFoundError(
            f"Raw data file was not found at: {path}"
        )

    df = pd.read_csv(path, low_memory=False)
    validate_raw_data(df)
    return df


def clean_raw_data(df: pd.DataFrame) -> pd.DataFrame:
    """Standardize types and whitespace without altering the source file."""

    cleaned = df.copy()

    for column in TEXT_COLUMNS:
        cleaned[column] = (
            cleaned[column]
            .astype("string")
            .str.strip()
            .replace("", pd.NA)
        )

    cleaned["Record_ID"] = pd.to_numeric(
        cleaned["Record_ID"],
        errors="raise",
    ).astype("int64")

    for column in NUMERIC_COLUMNS:
        cleaned[column] = pd.to_numeric(
            cleaned[column],
            errors="raise",
        )

    cleaned["Observation_Date"] = pd.to_datetime(
        cleaned["Observation_Date"],
        errors="coerce",
    )

    return cleaned


def add_analytical_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add documented fields used by SQL and dashboard analyses."""

    enriched = df.copy()

    # Scientific_Name is the stable taxon key. The Species field contains
    # only the epithet and is shared by some unrelated genera.
    enriched["Taxon_ID"] = enriched["Scientific_Name"]

    enriched["Observation_Year"] = (
        enriched["Observation_Date"].dt.year.astype("Int64")
    )
    enriched["Observation_Month"] = (
        enriched["Observation_Date"].dt.month.astype("Int64")
    )
    enriched["Observation_Month_Name"] = (
        enriched["Observation_Date"].dt.month_name().astype("string")
    )
    enriched["Observation_Quarter"] = (
        enriched["Observation_Date"].dt.quarter.astype("Int64")
    )

    enriched["IUCN_Risk_Score"] = (
        enriched["IUCN_Status"]
        .map(IUCN_RISK_SCORES)
        .astype("Int64")
    )
    enriched["Is_Threatened"] = (
        enriched["IUCN_Status"].isin(THREATENED_STATUSES)
    )
    enriched["Conservation_Group"] = np.select(
        [
            enriched["IUCN_Status"].isin(THREATENED_STATUSES),
            enriched["IUCN_Status"].eq("Near Threatened"),
            enriched["IUCN_Status"].eq("Least Concern"),
        ],
        [
            "Threatened",
            "Near Threatened",
            "Least Concern",
        ],
        default="Unassessed or uncertain",
    )

    enriched["Depth_Range_m"] = (
        enriched["Depth_Max_m"] - enriched["Depth_Min_m"]
    )
    enriched["Relative_Depth_Position"] = np.where(
        enriched["Depth_Range_m"] > 0,
        (
            enriched["Obs_Depth_m"] - enriched["Depth_Min_m"]
        )
        / enriched["Depth_Range_m"],
        0.0,
    )

    enriched["Depth_Band"] = pd.cut(
        enriched["Obs_Depth_m"],
        bins=DEPTH_BINS,
        labels=DEPTH_LABELS,
        include_lowest=True,
    )

    enriched["Body_Length_Band"] = pd.cut(
        enriched["Body_Length_cm"],
        bins=BODY_LENGTH_BINS,
        labels=BODY_LENGTH_LABELS,
        include_lowest=True,
    )

    enriched["Log_Body_Length_cm"] = np.log1p(
        enriched["Body_Length_cm"]
    )
    enriched["Log_Body_Weight_kg"] = np.log1p(
        enriched["Body_Weight_kg"]
    )

    enriched["Latitude_Zone"] = pd.cut(
        enriched["Latitude"].abs(),
        bins=[0, 23.5, 35, 55, 66.5, 90],
        labels=[
            "Tropical",
            "Subtropical",
            "Temperate",
            "Subpolar",
            "Polar",
        ],
        include_lowest=True,
    )

    enriched["Hemisphere"] = np.select(
        [
            enriched["Latitude"] > 0,
            enriched["Latitude"] < 0,
        ],
        [
            "Northern",
            "Southern",
        ],
        default="Equatorial",
    )

    return enriched


def prepare_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """Run the complete transformation pipeline."""

    cleaned = clean_raw_data(df)
    return add_analytical_features(cleaned)


def build_species_reference(df: pd.DataFrame) -> pd.DataFrame:
    """Build one summary row per full scientific name."""

    reference = (
        df.groupby("Scientific_Name", as_index=False, observed=True)
        .agg(
            Common_Name=("Common_Name", "first"),
            Kingdom=("Kingdom", "first"),
            Phylum=("Phylum", "first"),
            Class=("Class", "first"),
            Order=("Order", "first"),
            Family=("Family", "first"),
            Genus=("Genus", "first"),
            Species_Epithet=("Species", "first"),
            Habitat_Type=("Habitat_Type", "first"),
            Diet=("Diet", "first"),
            IUCN_Status=("IUCN_Status", "first"),
            IUCN_Risk_Score=("IUCN_Risk_Score", "first"),
            Is_Threatened=("Is_Threatened", "first"),
            Conservation_Group=("Conservation_Group", "first"),
            Primary_Biome=("Biome", "first"),
            Depth_Min_m=("Depth_Min_m", "min"),
            Depth_Max_m=("Depth_Max_m", "max"),
            Observation_Count=("Record_ID", "count"),
            Location_Count=("Location", "nunique"),
            Biome_Count=("Biome", "nunique"),
            Mean_Observed_Depth_m=("Obs_Depth_m", "mean"),
            Median_Observed_Depth_m=("Obs_Depth_m", "median"),
            Mean_Body_Length_cm=("Body_Length_cm", "mean"),
            Median_Body_Length_cm=("Body_Length_cm", "median"),
            Mean_Body_Weight_kg=("Body_Weight_kg", "mean"),
            Median_Body_Weight_kg=("Body_Weight_kg", "median"),
            Mean_Estimated_Age_yr=("Estimated_Age_yr", "mean"),
            Mean_Water_Temp_C=("Water_Temp_C", "mean"),
            Mean_Salinity_ppt=("Salinity_ppt", "mean"),
            Mean_pH=("pH", "mean"),
            First_Observation_Date=("Observation_Date", "min"),
            Last_Observation_Date=("Observation_Date", "max"),
            Fun_Fact=("Fun_Fact", "first"),
        )
        .sort_values(["Common_Name", "Scientific_Name"])
        .reset_index(drop=True)
    )

    rounded_columns = reference.select_dtypes(
        include=["float64", "float32"]
    ).columns
    reference[rounded_columns] = reference[rounded_columns].round(4)

    return reference
