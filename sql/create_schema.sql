PRAGMA foreign_keys = ON;

DROP TABLE IF EXISTS pipeline_metadata;
DROP TABLE IF EXISTS observations;
DROP TABLE IF EXISTS species_reference;

CREATE TABLE species_reference (
    Scientific_Name TEXT PRIMARY KEY,
    Common_Name TEXT NOT NULL,
    Kingdom TEXT,
    Phylum TEXT,
    Class TEXT,
    "Order" TEXT,
    Family TEXT,
    Genus TEXT,
    Species_Epithet TEXT,
    Habitat_Type TEXT,
    Diet TEXT,
    IUCN_Status TEXT,
    IUCN_Risk_Score INTEGER,
    Is_Threatened INTEGER NOT NULL CHECK (Is_Threatened IN (0, 1)),
    Conservation_Group TEXT,
    Primary_Biome TEXT,
    Depth_Min_m REAL,
    Depth_Max_m REAL,
    Observation_Count INTEGER,
    Location_Count INTEGER,
    Biome_Count INTEGER,
    Mean_Observed_Depth_m REAL,
    Median_Observed_Depth_m REAL,
    Mean_Body_Length_cm REAL,
    Median_Body_Length_cm REAL,
    Mean_Body_Weight_kg REAL,
    Median_Body_Weight_kg REAL,
    Mean_Estimated_Age_yr REAL,
    Mean_Water_Temp_C REAL,
    Mean_Salinity_ppt REAL,
    Mean_pH REAL,
    First_Observation_Date TEXT,
    Last_Observation_Date TEXT,
    Fun_Fact TEXT
);

CREATE TABLE observations (
    Record_ID INTEGER PRIMARY KEY,
    Common_Name TEXT NOT NULL,
    Scientific_Name TEXT NOT NULL,
    Kingdom TEXT,
    Phylum TEXT,
    Class TEXT,
    "Order" TEXT,
    Family TEXT,
    Genus TEXT,
    Species TEXT,
    Habitat_Type TEXT,
    Depth_Min_m REAL,
    Depth_Max_m REAL,
    Obs_Depth_m REAL,
    Location TEXT,
    Latitude REAL CHECK (Latitude BETWEEN -90 AND 90),
    Longitude REAL CHECK (Longitude BETWEEN -180 AND 180),
    Diet TEXT,
    IUCN_Status TEXT,
    Estimated_Age_yr REAL,
    Body_Length_cm REAL,
    Body_Weight_kg REAL,
    Sex TEXT,
    Water_Temp_C REAL,
    Salinity_ppt REAL,
    pH REAL,
    Observation_Date TEXT,
    Observation_Method TEXT,
    Biome TEXT,
    Fun_Fact TEXT,
    Taxon_ID TEXT NOT NULL,
    Observation_Year INTEGER,
    Observation_Month INTEGER,
    Observation_Month_Name TEXT,
    Observation_Quarter INTEGER,
    IUCN_Risk_Score INTEGER,
    Is_Threatened INTEGER NOT NULL CHECK (Is_Threatened IN (0, 1)),
    Conservation_Group TEXT,
    Depth_Range_m REAL,
    Relative_Depth_Position REAL,
    Depth_Band TEXT,
    Body_Length_Band TEXT,
    Log_Body_Length_cm REAL,
    Log_Body_Weight_kg REAL,
    Latitude_Zone TEXT,
    Hemisphere TEXT,
    FOREIGN KEY (Taxon_ID)
        REFERENCES species_reference (Scientific_Name)
);

CREATE TABLE pipeline_metadata (
    Key TEXT PRIMARY KEY,
    Value TEXT NOT NULL
);

CREATE INDEX idx_observations_taxon
    ON observations (Taxon_ID);

CREATE INDEX idx_observations_date
    ON observations (Observation_Date);

CREATE INDEX idx_observations_year
    ON observations (Observation_Year);

CREATE INDEX idx_observations_location
    ON observations (Location);

CREATE INDEX idx_observations_biome
    ON observations (Biome);

CREATE INDEX idx_observations_habitat
    ON observations (Habitat_Type);

CREATE INDEX idx_observations_iucn
    ON observations (IUCN_Status);

CREATE INDEX idx_observations_method
    ON observations (Observation_Method);
