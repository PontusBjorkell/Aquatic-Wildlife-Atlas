"""Prepare analysis-ready aquatic wildlife datasets."""

from __future__ import annotations

import json
import logging

from aquatic_wildlife.config import (
    DATA_QUALITY_REPORT_PATH,
    PROCESSED_DATA_PATH,
    RAW_DATA_PATH,
    SPECIES_REFERENCE_PATH,
    ensure_directories,
)
from aquatic_wildlife.data import (
    build_species_reference,
    load_raw_data,
    prepare_dataset,
)
from aquatic_wildlife.validation import build_quality_report


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Execute the full Phase 1 preprocessing pipeline."""

    ensure_directories()

    LOGGER.info("Loading raw data from %s", RAW_DATA_PATH)
    raw_df = load_raw_data()
    LOGGER.info(
        "Loaded %s rows and %d columns",
        f"{len(raw_df):,}",
        raw_df.shape[1],
    )

    LOGGER.info("Building data-quality report")
    quality_report = build_quality_report(raw_df)

    LOGGER.info("Cleaning data and adding analytical features")
    processed_df = prepare_dataset(raw_df)

    LOGGER.info("Building species reference table")
    species_reference = build_species_reference(processed_df)

    processed_df.to_csv(
        PROCESSED_DATA_PATH,
        index=False,
        date_format="%Y-%m-%d",
    )
    species_reference.to_csv(
        SPECIES_REFERENCE_PATH,
        index=False,
        date_format="%Y-%m-%d",
    )
    DATA_QUALITY_REPORT_PATH.write_text(
        json.dumps(
            quality_report,
            indent=2,
            ensure_ascii=False,
        ),
        encoding="utf-8",
    )

    LOGGER.info(
        "Saved processed observations: %s",
        PROCESSED_DATA_PATH,
    )
    LOGGER.info(
        "Saved %s-taxon reference table: %s",
        f"{len(species_reference):,}",
        SPECIES_REFERENCE_PATH,
    )
    LOGGER.info(
        "Saved data-quality report: %s",
        DATA_QUALITY_REPORT_PATH,
    )
    LOGGER.info("Phase 1 data preparation completed successfully")


if __name__ == "__main__":
    main()
