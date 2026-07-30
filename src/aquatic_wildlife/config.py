"""Central configuration for the Aquatic Wildlife Atlas project."""

from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]

DATA_DIR = PROJECT_ROOT / "data"
RAW_DATA_DIR = DATA_DIR / "raw"
PROCESSED_DATA_DIR = DATA_DIR / "processed"
DATABASE_DIR = DATA_DIR / "database"
ANALYSIS_RESULTS_DIR = DATA_DIR / "analysis_results"
DASHBOARD_DATA_DIR = DATA_DIR / "dashboard"

SQL_DIR = PROJECT_ROOT / "sql"
REPORTS_DIR = PROJECT_ROOT / "reports"
FIGURES_DIR = REPORTS_DIR / "figures"
SQL_REPORTS_DIR = REPORTS_DIR / "sql"
STATISTICAL_REPORTS_DIR = REPORTS_DIR / "statistical"

IMAGES_DIR = PROJECT_ROOT / "images"
STREAMLIT_IMAGES_DIR = IMAGES_DIR / "streamlit"
TABLEAU_IMAGES_DIR = IMAGES_DIR / "tableau"

RAW_DATA_PATH = RAW_DATA_DIR / "aquatic_animals_200k.csv"
PROCESSED_DATA_PATH = PROCESSED_DATA_DIR / "aquatic_wildlife_processed.csv"
SPECIES_REFERENCE_PATH = PROCESSED_DATA_DIR / "species_reference.csv"
DATA_QUALITY_REPORT_PATH = PROCESSED_DATA_DIR / "data_quality_report.json"

DATABASE_PATH = DATABASE_DIR / "aquatic_wildlife.db"
SCHEMA_SQL_PATH = SQL_DIR / "create_schema.sql"
VIEWS_SQL_PATH = SQL_DIR / "create_views.sql"
ANALYSIS_SQL_PATH = SQL_DIR / "analysis_queries.sql"

EXPECTED_COLUMNS = [
    "Record_ID",
    "Common_Name",
    "Scientific_Name",
    "Kingdom",
    "Phylum",
    "Class",
    "Order",
    "Family",
    "Genus",
    "Species",
    "Habitat_Type",
    "Depth_Min_m",
    "Depth_Max_m",
    "Obs_Depth_m",
    "Location",
    "Latitude",
    "Longitude",
    "Diet",
    "IUCN_Status",
    "Estimated_Age_yr",
    "Body_Length_cm",
    "Body_Weight_kg",
    "Sex",
    "Water_Temp_C",
    "Salinity_ppt",
    "pH",
    "Observation_Date",
    "Observation_Method",
    "Biome",
    "Fun_Fact",
]

REQUIRED_IDENTIFIER_COLUMNS = [
    "Record_ID",
    "Common_Name",
    "Scientific_Name",
]

NUMERIC_COLUMNS = [
    "Depth_Min_m",
    "Depth_Max_m",
    "Obs_Depth_m",
    "Latitude",
    "Longitude",
    "Estimated_Age_yr",
    "Body_Length_cm",
    "Body_Weight_kg",
    "Water_Temp_C",
    "Salinity_ppt",
    "pH",
]

TEXT_COLUMNS = [
    column
    for column in EXPECTED_COLUMNS
    if column not in NUMERIC_COLUMNS
    and column not in {"Record_ID", "Observation_Date"}
]

IUCN_STATUS_ORDER = [
    "Not Evaluated",
    "Data Deficient",
    "Least Concern",
    "Near Threatened",
    "Vulnerable",
    "Endangered",
    "Critically Endangered",
]

THREATENED_STATUSES = {
    "Vulnerable",
    "Endangered",
    "Critically Endangered",
}

IUCN_RISK_SCORES = {
    "Not Evaluated": 0,
    "Data Deficient": 1,
    "Least Concern": 2,
    "Near Threatened": 3,
    "Vulnerable": 4,
    "Endangered": 5,
    "Critically Endangered": 6,
}

DEPTH_BINS = [
    float("-inf"),
    10,
    50,
    200,
    1_000,
    4_000,
    float("inf"),
]

DEPTH_LABELS = [
    "Very shallow (≤10 m)",
    "Shallow (10–50 m)",
    "Shelf (50–200 m)",
    "Upper deep sea (200–1,000 m)",
    "Deep sea (1,000–4,000 m)",
    "Hadal/very deep (>4,000 m)",
]

BODY_LENGTH_BINS = [
    float("-inf"),
    10,
    50,
    100,
    300,
    1_000,
    float("inf"),
]

BODY_LENGTH_LABELS = [
    "Very small (≤10 cm)",
    "Small (10–50 cm)",
    "Medium (50–100 cm)",
    "Large (100–300 cm)",
    "Very large (300–1,000 cm)",
    "Giant (>1,000 cm)",
]


def ensure_directories() -> None:
    """Create all project output directories if they do not exist."""

    directories = [
        RAW_DATA_DIR,
        PROCESSED_DATA_DIR,
        DATABASE_DIR,
        ANALYSIS_RESULTS_DIR,
        DASHBOARD_DATA_DIR,
        FIGURES_DIR,
        SQL_REPORTS_DIR,
        STATISTICAL_REPORTS_DIR,
        STREAMLIT_IMAGES_DIR,
        TABLEAU_IMAGES_DIR,
    ]

    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)
