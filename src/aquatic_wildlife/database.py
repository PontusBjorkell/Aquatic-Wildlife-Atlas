"""SQLite warehouse creation and validation utilities."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from aquatic_wildlife.config import (
    DATABASE_PATH,
    PROCESSED_DATA_PATH,
    SCHEMA_SQL_PATH,
    SPECIES_REFERENCE_PATH,
    VIEWS_SQL_PATH,
)


def connect_database(path: Path = DATABASE_PATH) -> sqlite3.Connection:
    """Open a SQLite connection with integrity features enabled."""

    connection = sqlite3.connect(path)
    connection.execute("PRAGMA foreign_keys = ON;")
    connection.execute("PRAGMA journal_mode = WAL;")
    connection.execute("PRAGMA synchronous = NORMAL;")
    return connection


def execute_sql_file(
    connection: sqlite3.Connection,
    sql_path: Path,
) -> None:
    """Execute a complete SQL script."""

    if not sql_path.exists():
        raise FileNotFoundError(f"SQL file was not found: {sql_path}")

    connection.executescript(sql_path.read_text(encoding="utf-8"))


def _prepare_for_sqlite(df: pd.DataFrame) -> pd.DataFrame:
    """Convert pandas extension types to SQLite-compatible values."""

    prepared = df.copy()

    for column in prepared.columns:
        if pd.api.types.is_datetime64_any_dtype(prepared[column]):
            prepared[column] = prepared[column].dt.strftime("%Y-%m-%d")
        elif pd.api.types.is_bool_dtype(prepared[column]):
            prepared[column] = prepared[column].astype("int64")
        elif isinstance(prepared[column].dtype, pd.CategoricalDtype):
            prepared[column] = prepared[column].astype("string")

    return prepared.where(pd.notna(prepared), None)


def load_table(
    connection: sqlite3.Connection,
    df: pd.DataFrame,
    table_name: str,
) -> None:
    """Append a dataframe to an existing explicitly defined table."""

    prepared = _prepare_for_sqlite(df)
    prepared.to_sql(
        table_name,
        connection,
        if_exists="append",
        index=False,
        chunksize=5_000,
    )


def validate_database(connection: sqlite3.Connection) -> dict[str, int]:
    """Check row counts, foreign keys, and SQLite integrity."""

    observation_count = connection.execute(
        "SELECT COUNT(*) FROM observations"
    ).fetchone()[0]
    taxon_count = connection.execute(
        "SELECT COUNT(*) FROM species_reference"
    ).fetchone()[0]
    orphan_count = connection.execute(
        """
        SELECT COUNT(*)
        FROM observations AS o
        LEFT JOIN species_reference AS s
            ON o.Taxon_ID = s.Scientific_Name
        WHERE s.Scientific_Name IS NULL
        """
    ).fetchone()[0]
    foreign_key_violations = len(
        connection.execute("PRAGMA foreign_key_check").fetchall()
    )
    integrity_result = connection.execute(
        "PRAGMA integrity_check"
    ).fetchone()[0]

    if observation_count == 0:
        raise RuntimeError("The observations table is empty.")
    if taxon_count == 0:
        raise RuntimeError("The species_reference table is empty.")
    if orphan_count:
        raise RuntimeError(
            f"Found {orphan_count:,} observations without a taxon."
        )
    if foreign_key_violations:
        raise RuntimeError(
            f"Found {foreign_key_violations:,} foreign-key violations."
        )
    if integrity_result != "ok":
        raise RuntimeError(
            f"SQLite integrity check failed: {integrity_result}"
        )

    return {
        "observations": int(observation_count),
        "taxa": int(taxon_count),
        "orphan_observations": int(orphan_count),
        "foreign_key_violations": int(foreign_key_violations),
    }


def build_database(
    processed_path: Path = PROCESSED_DATA_PATH,
    species_reference_path: Path = SPECIES_REFERENCE_PATH,
    database_path: Path = DATABASE_PATH,
    schema_path: Path = SCHEMA_SQL_PATH,
    views_path: Path = VIEWS_SQL_PATH,
) -> dict[str, int]:
    """Build the complete SQLite warehouse from processed CSV exports."""

    for path in (processed_path, species_reference_path):
        if not path.exists():
            raise FileNotFoundError(
                f"Required processed file was not found: {path}. "
                "Run scripts/prepare_data.py first."
            )

    observations = pd.read_csv(
        processed_path,
        parse_dates=["Observation_Date"],
        low_memory=False,
    )
    species_reference = pd.read_csv(
        species_reference_path,
        parse_dates=[
            "First_Observation_Date",
            "Last_Observation_Date",
        ],
    )

    database_path.parent.mkdir(parents=True, exist_ok=True)
    database_path.unlink(missing_ok=True)

    connection = connect_database(database_path)

    try:
        execute_sql_file(connection, schema_path)

        # Parent table must be loaded before the observation fact table.
        load_table(connection, species_reference, "species_reference")
        load_table(connection, observations, "observations")

        metadata = [
            ("built_at_utc", datetime.now(timezone.utc).isoformat()),
            ("source_observation_rows", str(len(observations))),
            ("source_taxon_rows", str(len(species_reference))),
            ("taxon_key", "Scientific_Name"),
            (
                "data_scope",
                "Educational dataset with synthetic-pattern caveats",
            ),
        ]
        connection.executemany(
            "INSERT INTO pipeline_metadata (Key, Value) VALUES (?, ?)",
            metadata,
        )

        execute_sql_file(connection, views_path)
        connection.commit()

        return validate_database(connection)
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()
