"""Taxon-level statistical analyses for the Aquatic Wildlife Atlas."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from itertools import combinations
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

from aquatic_wildlife.config import (
    SPECIES_REFERENCE_PATH,
    STATISTICAL_REPORTS_DIR,
)


NUMERIC_METRICS = [
    "Mean_Observed_Depth_m",
    "Mean_Body_Length_cm",
    "Mean_Body_Weight_kg",
    "Mean_Estimated_Age_yr",
    "Mean_Water_Temp_C",
    "Mean_Salinity_ppt",
    "Mean_pH",
    "Location_Count",
]

GROUP_COMPARISON_METRICS = [
    "Mean_Observed_Depth_m",
    "Mean_Body_Length_cm",
    "Mean_Body_Weight_kg",
    "Mean_Estimated_Age_yr",
    "Mean_Water_Temp_C",
    "Mean_Salinity_ppt",
    "Mean_pH",
]


def benjamini_hochberg(p_values: pd.Series) -> pd.Series:
    """Apply Benjamini-Hochberg false-discovery-rate correction."""

    values = pd.to_numeric(p_values, errors="coerce").to_numpy(float)
    adjusted = np.full(len(values), np.nan)
    valid_positions = np.flatnonzero(np.isfinite(values))

    if not len(valid_positions):
        return pd.Series(adjusted, index=p_values.index)

    valid_values = values[valid_positions]
    order = np.argsort(valid_values)
    ranked = valid_values[order]
    count = len(ranked)

    corrected = ranked * count / np.arange(1, count + 1)
    corrected = np.minimum.accumulate(corrected[::-1])[::-1]
    corrected = np.clip(corrected, 0, 1)

    restored = np.empty(count)
    restored[order] = corrected
    adjusted[valid_positions] = restored

    return pd.Series(adjusted, index=p_values.index)


def descriptive_statistics(df: pd.DataFrame) -> pd.DataFrame:
    """Return taxon-level descriptive statistics for numeric metrics."""

    rows = []
    for metric in NUMERIC_METRICS:
        values = pd.to_numeric(df[metric], errors="coerce").dropna()
        rows.append(
            {
                "Metric": metric,
                "N_Taxa": int(len(values)),
                "Mean": values.mean(),
                "Standard_Deviation": values.std(ddof=1),
                "Minimum": values.min(),
                "Q1": values.quantile(0.25),
                "Median": values.median(),
                "Q3": values.quantile(0.75),
                "Maximum": values.max(),
                "IQR": values.quantile(0.75) - values.quantile(0.25),
            }
        )
    return pd.DataFrame(rows).round(6)


def spearman_analysis(
    df: pd.DataFrame,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Calculate Spearman correlations, p-values, and pairwise results."""

    numeric = df[NUMERIC_METRICS].apply(pd.to_numeric, errors="coerce")
    correlation = numeric.corr(method="spearman")
    pvalue_matrix = pd.DataFrame(
        np.nan,
        index=NUMERIC_METRICS,
        columns=NUMERIC_METRICS,
    )
    pair_rows = []

    for first, second in combinations(NUMERIC_METRICS, 2):
        complete = numeric[[first, second]].dropna()
        coefficient, p_value = stats.spearmanr(
            complete[first],
            complete[second],
        )
        pvalue_matrix.loc[first, second] = p_value
        pvalue_matrix.loc[second, first] = p_value
        pair_rows.append(
            {
                "Metric_1": first,
                "Metric_2": second,
                "N_Taxa": len(complete),
                "Spearman_Rho": coefficient,
                "P_Value": p_value,
            }
        )

    np.fill_diagonal(pvalue_matrix.values, 0.0)
    pairs = pd.DataFrame(pair_rows)
    pairs["Adjusted_P_Value"] = benjamini_hochberg(pairs["P_Value"])
    pairs["Significant_FDR_0_05"] = pairs["Adjusted_P_Value"] < 0.05
    pairs["Absolute_Rho"] = pairs["Spearman_Rho"].abs()
    pairs = pairs.sort_values(
        ["Absolute_Rho", "Adjusted_P_Value"],
        ascending=[False, True],
    ).reset_index(drop=True)

    return (
        correlation.round(6),
        pvalue_matrix,
        pairs,
    )


def threatened_group_comparisons(df: pd.DataFrame) -> pd.DataFrame:
    """Compare threatened and non-threatened taxa using Mann-Whitney U."""

    rows = []

    for metric in GROUP_COMPARISON_METRICS:
        threatened = pd.to_numeric(
            df.loc[df["Is_Threatened"].astype(bool), metric],
            errors="coerce",
        ).dropna()
        other = pd.to_numeric(
            df.loc[~df["Is_Threatened"].astype(bool), metric],
            errors="coerce",
        ).dropna()

        u_statistic, p_value = stats.mannwhitneyu(
            threatened,
            other,
            alternative="two-sided",
        )
        rank_biserial = (
            2 * u_statistic / (len(threatened) * len(other)) - 1
        )

        rows.append(
            {
                "Metric": metric,
                "Threatened_N": len(threatened),
                "Other_N": len(other),
                "Threatened_Median": threatened.median(),
                "Other_Median": other.median(),
                "Mann_Whitney_U": u_statistic,
                "P_Value": p_value,
                "Rank_Biserial_Correlation": rank_biserial,
            }
        )

    result = pd.DataFrame(rows)
    result["Adjusted_P_Value"] = benjamini_hochberg(result["P_Value"])
    result["Significant_FDR_0_05"] = result["Adjusted_P_Value"] < 0.05
    return result


def habitat_comparisons(df: pd.DataFrame) -> pd.DataFrame:
    """Compare metrics across habitats with Kruskal-Wallis tests."""

    eligible_habitats = (
        df["Habitat_Type"].value_counts()
        .loc[lambda counts: counts >= 2]
        .index
    )
    subset = df[df["Habitat_Type"].isin(eligible_habitats)]
    rows = []

    for metric in GROUP_COMPARISON_METRICS:
        groups = [
            pd.to_numeric(group[metric], errors="coerce").dropna()
            for _, group in subset.groupby("Habitat_Type")
        ]
        groups = [group for group in groups if len(group) >= 2]

        statistic, p_value = stats.kruskal(*groups)
        sample_size = sum(len(group) for group in groups)
        group_count = len(groups)
        epsilon_squared = max(
            0.0,
            (statistic - group_count + 1)
            / (sample_size - group_count),
        )

        rows.append(
            {
                "Metric": metric,
                "Habitat_Group_Count": group_count,
                "N_Taxa": sample_size,
                "Kruskal_Wallis_H": statistic,
                "Degrees_Of_Freedom": group_count - 1,
                "P_Value": p_value,
                "Epsilon_Squared": epsilon_squared,
            }
        )

    result = pd.DataFrame(rows)
    result["Adjusted_P_Value"] = benjamini_hochberg(result["P_Value"])
    result["Significant_FDR_0_05"] = result["Adjusted_P_Value"] < 0.05
    return result


def _bias_corrected_cramers_v(table: pd.DataFrame) -> float:
    """Calculate bias-corrected Cramér's V for a contingency table."""

    chi_square = stats.chi2_contingency(table, correction=False)[0]
    n = table.to_numpy().sum()
    rows, columns = table.shape
    phi_squared = chi_square / n
    corrected_phi = max(
        0.0,
        phi_squared - ((columns - 1) * (rows - 1)) / (n - 1),
    )
    corrected_rows = rows - ((rows - 1) ** 2) / (n - 1)
    corrected_columns = columns - ((columns - 1) ** 2) / (n - 1)
    denominator = min(corrected_columns - 1, corrected_rows - 1)
    return np.sqrt(corrected_phi / denominator) if denominator > 0 else 0.0


def categorical_associations(df: pd.DataFrame) -> pd.DataFrame:
    """Test taxon-level associations between conservation and ecology."""

    pairs = [
        ("IUCN_Status", "Class"),
        ("IUCN_Status", "Habitat_Type"),
        ("IUCN_Status", "Diet"),
        ("Is_Threatened", "Class"),
        ("Is_Threatened", "Habitat_Type"),
        ("Is_Threatened", "Diet"),
        ("Habitat_Type", "Diet"),
    ]
    rows = []

    for first, second in pairs:
        table = pd.crosstab(df[first], df[second])
        chi_square, p_value, degrees_freedom, expected = (
            stats.chi2_contingency(table, correction=False)
        )
        rows.append(
            {
                "Variable_1": first,
                "Variable_2": second,
                "N_Taxa": int(table.to_numpy().sum()),
                "Rows": table.shape[0],
                "Columns": table.shape[1],
                "Chi_Square": chi_square,
                "Degrees_Of_Freedom": degrees_freedom,
                "P_Value": p_value,
                "Bias_Corrected_Cramers_V": (
                    _bias_corrected_cramers_v(table)
                ),
                "Expected_Cells_Below_5_Percentage": (
                    100.0 * (expected < 5).sum() / expected.size
                ),
                "Sparse_Table_Warning": bool((expected < 5).mean() > 0.20),
            }
        )

    result = pd.DataFrame(rows)
    result["Adjusted_P_Value"] = benjamini_hochberg(result["P_Value"])
    result["Significant_FDR_0_05"] = result["Adjusted_P_Value"] < 0.05
    return result


def allometric_regression(df: pd.DataFrame) -> pd.DataFrame:
    """Estimate taxon-level log-weight/log-length allometry."""

    data = df[
        ["Mean_Body_Length_cm", "Mean_Body_Weight_kg"]
    ].dropna()
    data = data[
        (data["Mean_Body_Length_cm"] > 0)
        & (data["Mean_Body_Weight_kg"] > 0)
    ]

    log_length = np.log10(data["Mean_Body_Length_cm"])
    log_weight = np.log10(data["Mean_Body_Weight_kg"])
    regression = stats.linregress(log_length, log_weight)

    return pd.DataFrame(
        [
            {
                "Model": (
                    "log10(Mean_Body_Weight_kg) ~ "
                    "log10(Mean_Body_Length_cm)"
                ),
                "N_Taxa": len(data),
                "Intercept": regression.intercept,
                "Slope": regression.slope,
                "R_Squared": regression.rvalue**2,
                "P_Value": regression.pvalue,
                "Slope_Standard_Error": regression.stderr,
                "Intercept_Standard_Error": regression.intercept_stderr,
            }
        ]
    )


def _build_markdown_report(
    df: pd.DataFrame,
    correlation_pairs: pd.DataFrame,
    threat_tests: pd.DataFrame,
    habitat_tests: pd.DataFrame,
    associations: pd.DataFrame,
    regression: pd.DataFrame,
) -> str:
    """Create a concise, reproducible statistical interpretation."""

    strongest = correlation_pairs.iloc[0]
    allometry = regression.iloc[0]
    significant_correlations = int(
        correlation_pairs["Significant_FDR_0_05"].sum()
    )
    significant_threat = int(
        threat_tests["Significant_FDR_0_05"].sum()
    )
    significant_habitat = int(
        habitat_tests["Significant_FDR_0_05"].sum()
    )
    significant_associations = int(
        associations["Significant_FDR_0_05"].sum()
    )

    return f"""# Statistical Analysis Report

## Scope

The analysis uses **{len(df)} full scientific-name taxa** as its units. The
200,000 observation records are intentionally not treated as independent
biological replicates because the dataset contains strong template-generated
patterns.

## Methods

- Taxon-level descriptive statistics
- Spearman rank correlations
- Mann–Whitney U tests for threatened versus other taxa
- Kruskal–Wallis tests across adequately represented habitat groups
- Chi-square tests with bias-corrected Cramér's V
- Log-log allometric regression of body weight on body length
- Benjamini–Hochberg false-discovery-rate correction within each test family

## Main numerical results

- Significant Spearman relationships after FDR correction:
  **{significant_correlations}**
- Strongest absolute Spearman relationship:
  **{strongest['Metric_1']} × {strongest['Metric_2']}**
  (rho = {strongest['Spearman_Rho']:.3f})
- Significant threatened/non-threatened comparisons:
  **{significant_threat}**
- Significant habitat comparisons:
  **{significant_habitat}**
- Significant categorical associations:
  **{significant_associations}**
- Allometric slope:
  **{allometry['Slope']:.3f}**
- Allometric R²:
  **{allometry['R_Squared']:.3f}**

## Interpretation boundary

These results describe internal structure in the supplied educational dataset.
They must not be interpreted as population estimates, causal ecological
effects, or independently verified biological findings. Taxonomy may also
create dependence among taxa, which this exploratory analysis does not model
phylogenetically.
"""


def run_statistical_analysis(
    species_reference_path: Path = SPECIES_REFERENCE_PATH,
    output_dir: Path = STATISTICAL_REPORTS_DIR,
) -> dict[str, object]:
    """Run and export the complete taxon-level statistical workflow."""

    if not species_reference_path.exists():
        raise FileNotFoundError(
            f"Species reference file was not found: {species_reference_path}. "
            "Run scripts/prepare_data.py first."
        )

    df = pd.read_csv(species_reference_path)
    if df["Scientific_Name"].duplicated().any():
        raise ValueError(
            "Species reference must contain one row per scientific name."
        )

    output_dir.mkdir(parents=True, exist_ok=True)

    descriptive = descriptive_statistics(df)
    correlation, pvalues, correlation_pairs = spearman_analysis(df)
    threat_tests = threatened_group_comparisons(df)
    habitat_tests = habitat_comparisons(df)
    associations = categorical_associations(df)
    regression = allometric_regression(df)

    exports = {
        "taxon_descriptive_statistics.csv": descriptive,
        "spearman_correlation_matrix.csv": correlation,
        "spearman_pvalue_matrix.csv": pvalues,
        "spearman_pairwise_results.csv": correlation_pairs,
        "threat_group_comparisons.csv": threat_tests,
        "habitat_kruskal_wallis.csv": habitat_tests,
        "categorical_associations.csv": associations,
        "allometric_regression.csv": regression,
    }

    for filename, result in exports.items():
        result.to_csv(output_dir / filename, index=True if "matrix" in filename else False)

    report = _build_markdown_report(
        df,
        correlation_pairs,
        threat_tests,
        habitat_tests,
        associations,
        regression,
    )
    (output_dir / "statistical_report.md").write_text(
        report,
        encoding="utf-8",
    )

    summary = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "unit_of_analysis": "full scientific-name taxon",
        "taxon_count": int(len(df)),
        "output_count": len(exports) + 2,
        "significant_spearman_pairs_fdr_0_05": int(
            correlation_pairs["Significant_FDR_0_05"].sum()
        ),
        "significant_threat_comparisons_fdr_0_05": int(
            threat_tests["Significant_FDR_0_05"].sum()
        ),
        "significant_habitat_comparisons_fdr_0_05": int(
            habitat_tests["Significant_FDR_0_05"].sum()
        ),
        "significant_categorical_associations_fdr_0_05": int(
            associations["Significant_FDR_0_05"].sum()
        ),
        "synthetic_data_caveat": (
            "Results describe the supplied educational dataset and are not "
            "population estimates or causal ecological evidence."
        ),
    }
    (output_dir / "statistical_summary.json").write_text(
        json.dumps(summary, indent=2),
        encoding="utf-8",
    )

    return summary
