"""Create compact, deployment-ready datasets for Streamlit and Tableau."""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from aquatic_wildlife.config import DASHBOARD_DATA_DIR, DATABASE_PATH


EXPORT_QUERIES = {
    "executive_summary.csv": """
        SELECT
            (SELECT COUNT(*) FROM observations) AS Observation_Count,
            (SELECT COUNT(*) FROM species_reference) AS Taxon_Count,
            (SELECT COUNT(DISTINCT Class) FROM species_reference) AS Class_Count,
            (SELECT COUNT(DISTINCT Location) FROM observations) AS Location_Count,
            (SELECT COUNT(*) FROM species_reference WHERE Is_Threatened = 1)
                AS Threatened_Taxon_Count,
            (SELECT MIN(Observation_Date) FROM observations) AS Date_Min,
            (SELECT MAX(Observation_Date) FROM observations) AS Date_Max
    """,
    "species.csv": "SELECT * FROM species_reference ORDER BY Common_Name",
    "conservation.csv": """
        SELECT * FROM v_conservation_summary ORDER BY IUCN_Risk_Score
    """,
    "habitats.csv": """
        SELECT * FROM v_habitat_summary ORDER BY Taxon_Count DESC
    """,
    "annual_trends.csv": """
        SELECT * FROM v_annual_observation_trends ORDER BY Observation_Year
    """,
    "locations.csv": """
        SELECT * FROM v_location_coverage ORDER BY Observation_Count DESC
    """,
    "methods.csv": """
        SELECT * FROM v_observation_method_summary
        ORDER BY Observation_Count DESC
    """,
    "monthly.csv": """
        SELECT Observation_Month, Observation_Month_Name,
               COUNT(*) AS Observation_Count,
               COUNT(DISTINCT Taxon_ID) AS Taxon_Count,
               ROUND(AVG(Water_Temp_C), 2) AS Mean_Water_Temp_C
        FROM observations
        GROUP BY Observation_Month, Observation_Month_Name
        ORDER BY Observation_Month
    """,
    "biomes.csv": """
        SELECT Biome, COUNT(*) AS Observation_Count,
               COUNT(DISTINCT Taxon_ID) AS Taxon_Count,
               ROUND(AVG(Obs_Depth_m), 2) AS Mean_Depth_m,
               ROUND(AVG(Water_Temp_C), 2) AS Mean_Temperature_C,
               ROUND(AVG(Salinity_ppt), 2) AS Mean_Salinity_ppt,
               ROUND(AVG(pH), 3) AS Mean_pH
        FROM observations GROUP BY Biome ORDER BY Observation_Count DESC
    """,
    "depth_bands.csv": """
        SELECT Depth_Band, COUNT(*) AS Observation_Count,
               COUNT(DISTINCT Taxon_ID) AS Taxon_Count,
               ROUND(AVG(Water_Temp_C), 2) AS Mean_Water_Temp_C,
               ROUND(AVG(Salinity_ppt), 2) AS Mean_Salinity_ppt
        FROM observations GROUP BY Depth_Band ORDER BY MIN(Obs_Depth_m)
    """,
    "map_sample.csv": """
        SELECT Record_ID, Common_Name, Scientific_Name, Habitat_Type,
               IUCN_Status, Location, Latitude, Longitude, Biome,
               Obs_Depth_m, Water_Temp_C, Observation_Year
        FROM observations
        WHERE Record_ID % 8 = 1
        ORDER BY Record_ID
        LIMIT 25000
    """,
    "coordinate_quality.csv": """
        SELECT Location, COUNT(*) AS Observation_Count,
               ROUND(MIN(Latitude), 3) AS Min_Latitude,
               ROUND(MAX(Latitude), 3) AS Max_Latitude,
               ROUND(MAX(Latitude)-MIN(Latitude), 3) AS Latitude_Span,
               ROUND(MIN(Longitude), 3) AS Min_Longitude,
               ROUND(MAX(Longitude), 3) AS Max_Longitude,
               ROUND(MAX(Longitude)-MIN(Longitude), 3) AS Longitude_Span
        FROM observations GROUP BY Location
        ORDER BY Longitude_Span DESC
    """,
}


def export_dashboard_data(
    database_path: Path = DATABASE_PATH,
    output_dir: Path = DASHBOARD_DATA_DIR,
) -> pd.DataFrame:
    """Export every curated dashboard dataset and a manifest."""

    if not database_path.exists():
        raise FileNotFoundError(
            f"Database not found: {database_path}. "
            "Run scripts/build_database.py first."
        )

    output_dir.mkdir(parents=True, exist_ok=True)
    manifest_rows = []

    with sqlite3.connect(database_path) as connection:
        for filename, query in EXPORT_QUERIES.items():
            result = pd.read_sql_query(query, connection)
            result.to_csv(output_dir / filename, index=False)
            manifest_rows.append(
                {
                    "file": filename,
                    "rows": len(result),
                    "columns": result.shape[1],
                }
            )

    manifest = pd.DataFrame(manifest_rows)
    manifest.to_csv(output_dir / "dashboard_manifest.csv", index=False)
    metadata = {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "export_count": len(EXPORT_QUERIES),
        "map_sample_rows": int(
            manifest.loc[manifest["file"] == "map_sample.csv", "rows"].iloc[0]
        ),
        "map_sampling_rule": "Record_ID modulo 8 equals 1; maximum 25,000 rows",
        "caveat": (
            "The dataset shows strong synthetic/template-generated patterns. "
            "Dashboard results describe supplied records only."
        ),
    }
    (output_dir / "dashboard_metadata.json").write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )
    return manifest
