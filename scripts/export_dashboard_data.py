"""Export curated data files consumed by Streamlit and Tableau."""

import logging

from aquatic_wildlife.config import DASHBOARD_DATA_DIR, ensure_directories
from aquatic_wildlife.dashboard import export_dashboard_data

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
LOGGER = logging.getLogger(__name__)


def main() -> None:
    ensure_directories()
    manifest = export_dashboard_data()
    for row in manifest.itertuples(index=False):
        LOGGER.info("%-28s %s rows", row.file, f"{row.rows:,}")
    LOGGER.info(
        "All %d dashboard exports completed successfully",
        len(manifest),
    )


if __name__ == "__main__":
    main()
