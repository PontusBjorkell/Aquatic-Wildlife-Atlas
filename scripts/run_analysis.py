"""Execute the complete SQL catalogue and export all results."""

from __future__ import annotations

import logging

from aquatic_wildlife.analysis import run_sql_analyses
from aquatic_wildlife.config import (
    ANALYSIS_RESULTS_DIR,
    ANALYSIS_SQL_PATH,
    DATABASE_PATH,
    ensure_directories,
)


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Run and report the complete analysis catalogue."""

    ensure_directories()

    LOGGER.info("Database: %s", DATABASE_PATH)
    LOGGER.info("SQL catalogue: %s", ANALYSIS_SQL_PATH)
    LOGGER.info("Export directory: %s", ANALYSIS_RESULTS_DIR)

    manifest = run_sql_analyses()

    for row in manifest.itertuples(index=False):
        LOGGER.info(
            "[%02d] %-42s %s rows",
            row.position,
            row.query_name,
            f"{row.row_count:,}",
        )

    LOGGER.info(
        "All %d SQL analyses completed successfully",
        len(manifest),
    )


if __name__ == "__main__":
    main()
