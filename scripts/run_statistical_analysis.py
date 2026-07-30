"""Run the complete taxon-level statistical workflow."""

from __future__ import annotations

import logging

from aquatic_wildlife.config import (
    SPECIES_REFERENCE_PATH,
    STATISTICAL_REPORTS_DIR,
    ensure_directories,
)
from aquatic_wildlife.statistics import run_statistical_analysis


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Execute and summarize statistical analyses."""

    ensure_directories()

    LOGGER.info("Taxon input: %s", SPECIES_REFERENCE_PATH)
    LOGGER.info("Output directory: %s", STATISTICAL_REPORTS_DIR)

    summary = run_statistical_analysis()

    LOGGER.info("Analyzed %d taxa", summary["taxon_count"])
    LOGGER.info(
        "Significant FDR-adjusted Spearman pairs: %d",
        summary["significant_spearman_pairs_fdr_0_05"],
    )
    LOGGER.info(
        "Significant FDR-adjusted habitat comparisons: %d",
        summary["significant_habitat_comparisons_fdr_0_05"],
    )
    LOGGER.info("Statistical analysis completed successfully")


if __name__ == "__main__":
    main()
