"""Validation and data-quality diagnostics for the raw dataset."""

from __future__ import annotations

from typing import Any

import pandas as pd

from aquatic_wildlife.config import (
    EXPECTED_COLUMNS,
    IUCN_STATUS_ORDER,
    NUMERIC_COLUMNS,
    REQUIRED_IDENTIFIER_COLUMNS,
)


class DataValidationError(ValueError):
    """Raised when the raw data cannot be processed safely."""


def _python_scalar(value: Any) -> Any:
    """Convert pandas and NumPy scalar values to JSON-safe Python values."""

    if pd.isna(value):
        return None
    return value.item() if hasattr(value, "item") else value


def validate_required_schema(df: pd.DataFrame) -> None:
    """Raise an informative error when required columns are absent."""

    missing_columns = sorted(set(EXPECTED_COLUMNS) - set(df.columns))
    unexpected_columns = sorted(set(df.columns) - set(EXPECTED_COLUMNS))

    if missing_columns:
        raise DataValidationError(
            "Raw data is missing expected columns: "
            + ", ".join(missing_columns)
        )

    if unexpected_columns:
        raise DataValidationError(
            "Raw data contains unexpected columns: "
            + ", ".join(unexpected_columns)
        )


def validate_identifiers(df: pd.DataFrame) -> None:
    """Ensure record and taxon identifiers are usable."""

    null_counts = df[REQUIRED_IDENTIFIER_COLUMNS].isna().sum()
    null_columns = null_counts[null_counts > 0]

    if not null_columns.empty:
        details = ", ".join(
            f"{column}={count}"
            for column, count in null_columns.items()
        )
        raise DataValidationError(
            f"Required identifier columns contain missing values: {details}"
        )

    duplicate_ids = int(df["Record_ID"].duplicated().sum())
    if duplicate_ids:
        raise DataValidationError(
            f"Record_ID contains {duplicate_ids:,} duplicate values."
        )


def validate_numeric_conversion(df: pd.DataFrame) -> None:
    """Check that expected numeric columns can be parsed as numbers."""

    failures: dict[str, int] = {}

    for column in NUMERIC_COLUMNS:
        converted = pd.to_numeric(df[column], errors="coerce")
        invalid = int((converted.isna() & df[column].notna()).sum())
        if invalid:
            failures[column] = invalid

    if failures:
        details = ", ".join(
            f"{column}={count}"
            for column, count in failures.items()
        )
        raise DataValidationError(
            f"Numeric columns contain non-numeric values: {details}"
        )


def validate_raw_data(df: pd.DataFrame) -> None:
    """Run blocking validations required before preprocessing."""

    if df.empty:
        raise DataValidationError("Raw dataset contains no rows.")

    validate_required_schema(df)
    validate_identifiers(df)
    validate_numeric_conversion(df)


def build_quality_report(df: pd.DataFrame) -> dict[str, Any]:
    """Create a serializable report of quality checks and dataset caveats."""

    parsed_dates = pd.to_datetime(
        df["Observation_Date"],
        errors="coerce",
    )

    numeric = df[NUMERIC_COLUMNS].apply(
        pd.to_numeric,
        errors="coerce",
    )

    depth_outside_range = (
        (numeric["Obs_Depth_m"] < numeric["Depth_Min_m"])
        | (numeric["Obs_Depth_m"] > numeric["Depth_Max_m"])
    )

    scientific_names_per_epithet = (
        df.groupby("Species", dropna=False)["Scientific_Name"]
        .nunique(dropna=False)
        .sort_values(ascending=False)
    )

    ambiguous_epithets = {
        str(epithet): sorted(
            df.loc[df["Species"] == epithet, "Scientific_Name"]
            .dropna()
            .unique()
            .tolist()
        )
        for epithet in scientific_names_per_epithet[
            scientific_names_per_epithet > 1
        ].index
    }

    template_columns = [
        "Depth_Min_m",
        "Depth_Max_m",
        "Habitat_Type",
        "Diet",
        "IUCN_Status",
        "Biome",
        "Fun_Fact",
    ]

    constant_within_taxon = {
        column: int(
            (
                df.groupby("Scientific_Name", dropna=False)[column]
                .nunique(dropna=False)
                == 1
            ).sum()
        )
        for column in template_columns
    }

    iucn_values = sorted(
        str(value)
        for value in df["IUCN_Status"].dropna().unique()
    )

    unknown_iucn = sorted(set(iucn_values) - set(IUCN_STATUS_ORDER))

    return {
        "dataset_summary": {
            "rows": int(len(df)),
            "columns": int(df.shape[1]),
            "unique_record_ids": int(df["Record_ID"].nunique()),
            "unique_common_names": int(df["Common_Name"].nunique()),
            "unique_scientific_names": int(
                df["Scientific_Name"].nunique()
            ),
            "unique_species_epithets": int(df["Species"].nunique()),
            "date_min": (
                parsed_dates.min().date().isoformat()
                if parsed_dates.notna().any()
                else None
            ),
            "date_max": (
                parsed_dates.max().date().isoformat()
                if parsed_dates.notna().any()
                else None
            ),
        },
        "completeness": {
            "total_missing_cells": int(df.isna().sum().sum()),
            "missing_by_column": {
                column: int(count)
                for column, count in df.isna().sum().items()
            },
            "invalid_observation_dates": int(parsed_dates.isna().sum()),
        },
        "uniqueness": {
            "duplicate_record_ids": int(
                df["Record_ID"].duplicated().sum()
            ),
            "fully_duplicated_rows": int(df.duplicated().sum()),
        },
        "range_checks": {
            "invalid_latitudes": int(
                ((numeric["Latitude"] < -90)
                 | (numeric["Latitude"] > 90)).sum()
            ),
            "invalid_longitudes": int(
                ((numeric["Longitude"] < -180)
                 | (numeric["Longitude"] > 180)).sum()
            ),
            "negative_observation_depths": int(
                (numeric["Obs_Depth_m"] < 0).sum()
            ),
            "observation_depth_outside_stated_range": int(
                depth_outside_range.sum()
            ),
            "nonpositive_body_lengths": int(
                (numeric["Body_Length_cm"] <= 0).sum()
            ),
            "nonpositive_body_weights": int(
                (numeric["Body_Weight_kg"] <= 0).sum()
            ),
            "ph_outside_0_14": int(
                ((numeric["pH"] < 0) | (numeric["pH"] > 14)).sum()
            ),
            "negative_salinity": int(
                (numeric["Salinity_ppt"] < 0).sum()
            ),
        },
        "taxonomy_checks": {
            "ambiguous_species_epithet_count": len(ambiguous_epithets),
            "ambiguous_species_epithets": ambiguous_epithets,
            "scientific_name_is_recommended_taxon_key": True,
        },
        "category_checks": {
            "observed_iucn_statuses": iucn_values,
            "unknown_iucn_statuses": unknown_iucn,
        },
        "synthetic_pattern_indicators": {
            "taxon_count": int(df["Scientific_Name"].nunique()),
            "constant_within_taxon": constant_within_taxon,
            "observation_count_min_per_taxon": _python_scalar(
                df["Scientific_Name"].value_counts().min()
            ),
            "observation_count_max_per_taxon": _python_scalar(
                df["Scientific_Name"].value_counts().max()
            ),
            "no_missing_values": bool(
                df.isna().sum().sum() == 0
            ),
            "interpretation": (
                "The regular class counts, complete records, and attributes "
                "that are constant within taxa are consistent with a "
                "template-generated or synthetic dataset. Results should be "
                "described as patterns in the supplied data, not population "
                "estimates or real-world ecological evidence."
            ),
        },
    }
