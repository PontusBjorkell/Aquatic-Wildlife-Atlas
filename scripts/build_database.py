"""Build and validate the Aquatic Wildlife Atlas SQLite warehouse."""

from __future__ import annotations

import logging

from aquatic_wildlife.config import DATABASE_PATH, ensure_directories
from aquatic_wildlife.database import build_database


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def main() -> None:
    """Build the warehouse and report validated row counts."""

    ensure_directories()

    LOGGER.info("Building SQLite warehouse at %s", DATABASE_PATH)
    counts = build_database()

    LOGGER.info(
        "Loaded %s observations and %s taxa",
        f"{counts['observations']:,}",
        f"{counts['taxa']:,}",
    )
    LOGGER.info(
        "Foreign-key violations: %d",
        counts["foreign_key_violations"],
    )
    LOGGER.info("SQLite warehouse completed successfully")


if __name__ == "__main__":
    main()
