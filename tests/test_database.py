"""Tests for SQLite warehouse construction."""

import sqlite3
from pathlib import Path

import pandas as pd

from aquatic_wildlife.data import (
    build_species_reference,
    prepare_dataset,
)
from aquatic_wildlife.database import build_database
from tests.test_validation import make_raw_row


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def test_build_database_creates_tables_and_views(tmp_path):
    raw = pd.DataFrame(
        [
            make_raw_row(Record_ID=1),
            make_raw_row(
                Record_ID=2,
                Observation_Date="2024-02-20",
                Obs_Depth_m=30.0,
            ),
        ]
    )
    processed = prepare_dataset(raw)
    species = build_species_reference(processed)

    processed_path = tmp_path / "processed.csv"
    species_path = tmp_path / "species.csv"
    database_path = tmp_path / "test.db"

    processed.to_csv(processed_path, index=False)
    species.to_csv(species_path, index=False)

    counts = build_database(
        processed_path=processed_path,
        species_reference_path=species_path,
        database_path=database_path,
        schema_path=PROJECT_ROOT / "sql" / "create_schema.sql",
        views_path=PROJECT_ROOT / "sql" / "create_views.sql",
    )

    assert counts["observations"] == 2
    assert counts["taxa"] == 1
    assert counts["foreign_key_violations"] == 0

    with sqlite3.connect(database_path) as connection:
        view_names = {
            row[0]
            for row in connection.execute(
                """
                SELECT name
                FROM sqlite_master
                WHERE type = 'view'
                """
            )
        }
        annual_count = connection.execute(
            """
            SELECT Observation_Count
            FROM v_annual_observation_trends
            WHERE Observation_Year = 2024
            """
        ).fetchone()[0]

    assert "v_conservation_summary" in view_names
    assert "v_species_environment_profile" in view_names
    assert annual_count == 2


def test_conservation_view_counts_taxa_not_observations(tmp_path):
    raw = pd.DataFrame(
        [
            make_raw_row(Record_ID=1, IUCN_Status="Endangered"),
            make_raw_row(Record_ID=2, IUCN_Status="Endangered"),
        ]
    )
    processed = prepare_dataset(raw)
    species = build_species_reference(processed)

    processed_path = tmp_path / "processed.csv"
    species_path = tmp_path / "species.csv"
    database_path = tmp_path / "test.db"

    processed.to_csv(processed_path, index=False)
    species.to_csv(species_path, index=False)

    build_database(
        processed_path=processed_path,
        species_reference_path=species_path,
        database_path=database_path,
        schema_path=PROJECT_ROOT / "sql" / "create_schema.sql",
        views_path=PROJECT_ROOT / "sql" / "create_views.sql",
    )

    with sqlite3.connect(database_path) as connection:
        taxon_count, observation_count = connection.execute(
            """
            SELECT Taxon_Count, Observation_Count
            FROM v_conservation_summary
            WHERE IUCN_Status = 'Endangered'
            """
        ).fetchone()

    assert taxon_count == 1
    assert observation_count == 2
