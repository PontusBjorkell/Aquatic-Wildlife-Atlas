"""Tests for taxon-level statistical analysis utilities."""

import numpy as np
import pandas as pd

from aquatic_wildlife.statistics import (
    benjamini_hochberg,
    run_statistical_analysis,
)


def make_species_reference(n=30):
    """Create a varied synthetic taxon table for unit tests."""

    index = np.arange(1, n + 1)
    return pd.DataFrame(
        {
            "Scientific_Name": [f"Genus species_{i}" for i in index],
            "Is_Threatened": index % 3 == 0,
            "IUCN_Status": np.where(
                index % 3 == 0,
                "Vulnerable",
                "Least Concern",
            ),
            "Class": np.where(index % 2 == 0, "Class A", "Class B"),
            "Habitat_Type": np.where(
                index % 2 == 0,
                "Marine",
                "Freshwater",
            ),
            "Diet": np.where(index % 2 == 0, "Carnivore", "Omnivore"),
            "Mean_Observed_Depth_m": index * 5.0,
            "Mean_Body_Length_cm": index * 2.0,
            "Mean_Body_Weight_kg": (index * 2.0) ** 2.8 / 1000,
            "Mean_Estimated_Age_yr": index / 2,
            "Mean_Water_Temp_C": 30 - index / 3,
            "Mean_Salinity_ppt": np.where(
                index % 2 == 0,
                35.0,
                0.5,
            ),
            "Mean_pH": 7.0 + index / 100,
            "Location_Count": (index % 6) + 1,
        }
    )


def test_benjamini_hochberg_is_monotonic_by_rank():
    pvalues = pd.Series([0.001, 0.01, 0.04, 0.20])
    adjusted = benjamini_hochberg(pvalues)

    assert adjusted.between(0, 1).all()
    assert adjusted.iloc[0] <= adjusted.iloc[1]
    assert adjusted.iloc[1] <= adjusted.iloc[2]
    assert adjusted.iloc[2] <= adjusted.iloc[3]


def test_run_statistical_analysis_exports_all_outputs(tmp_path):
    input_path = tmp_path / "species_reference.csv"
    output_dir = tmp_path / "statistical"
    make_species_reference().to_csv(input_path, index=False)

    summary = run_statistical_analysis(
        species_reference_path=input_path,
        output_dir=output_dir,
    )

    expected_files = {
        "taxon_descriptive_statistics.csv",
        "spearman_correlation_matrix.csv",
        "spearman_pvalue_matrix.csv",
        "spearman_pairwise_results.csv",
        "threat_group_comparisons.csv",
        "habitat_kruskal_wallis.csv",
        "categorical_associations.csv",
        "allometric_regression.csv",
        "statistical_report.md",
        "statistical_summary.json",
    }

    assert summary["taxon_count"] == 30
    assert {path.name for path in output_dir.iterdir()} == expected_files


def test_duplicate_taxon_keys_are_rejected(tmp_path):
    input_path = tmp_path / "species_reference.csv"
    data = make_species_reference()
    data.loc[1, "Scientific_Name"] = data.loc[0, "Scientific_Name"]
    data.to_csv(input_path, index=False)

    try:
        run_statistical_analysis(
            species_reference_path=input_path,
            output_dir=tmp_path / "statistical",
        )
    except ValueError as error:
        assert "one row per scientific name" in str(error)
    else:
        raise AssertionError("Duplicate taxon keys should raise ValueError")
