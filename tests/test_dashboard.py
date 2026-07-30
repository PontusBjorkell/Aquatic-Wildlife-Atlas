"""Tests for deployment-ready dashboard exports."""

from pathlib import Path

import pandas as pd

from aquatic_wildlife.dashboard import EXPORT_QUERIES, export_dashboard_data


def test_dashboard_query_catalogue_has_expected_exports():
    assert len(EXPORT_QUERIES) == 12
    assert "species.csv" in EXPORT_QUERIES
    assert "map_sample.csv" in EXPORT_QUERIES


def test_dashboard_exports_from_project_database(tmp_path):
    project_root = Path(__file__).resolve().parents[1]
    database_path = project_root / "data" / "database" / "aquatic_wildlife.db"
    if not database_path.exists():
        return

    manifest = export_dashboard_data(
        database_path=database_path,
        output_dir=tmp_path,
    )

    assert len(manifest) == len(EXPORT_QUERIES)
    assert set(manifest["file"]) == set(EXPORT_QUERIES)
    assert (tmp_path / "dashboard_manifest.csv").exists()
    assert (tmp_path / "dashboard_metadata.json").exists()
    species = pd.read_csv(tmp_path / "species.csv")
    assert species["Scientific_Name"].nunique() == 101
