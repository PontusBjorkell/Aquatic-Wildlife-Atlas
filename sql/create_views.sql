DROP VIEW IF EXISTS v_observation_enriched;
DROP VIEW IF EXISTS v_conservation_summary;
DROP VIEW IF EXISTS v_species_environment_profile;
DROP VIEW IF EXISTS v_habitat_summary;
DROP VIEW IF EXISTS v_annual_observation_trends;
DROP VIEW IF EXISTS v_location_coverage;
DROP VIEW IF EXISTS v_observation_method_summary;

CREATE VIEW v_observation_enriched AS
SELECT
    o.*,
    s.Species_Epithet,
    s.Primary_Biome,
    s.Observation_Count AS Taxon_Observation_Count,
    s.Location_Count AS Taxon_Location_Count
FROM observations AS o
INNER JOIN species_reference AS s
    ON o.Taxon_ID = s.Scientific_Name;

-- Taxon-level conservation summary. Species counts are calculated from the
-- 101-row reference table rather than repeated observation records.
CREATE VIEW v_conservation_summary AS
SELECT
    IUCN_Status,
    IUCN_Risk_Score,
    Conservation_Group,
    COUNT(*) AS Taxon_Count,
    SUM(Observation_Count) AS Observation_Count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
        AS Taxon_Percentage,
    ROUND(AVG(Mean_Body_Length_cm), 2)
        AS Mean_Taxon_Body_Length_cm,
    ROUND(AVG(Mean_Body_Weight_kg), 2)
        AS Mean_Taxon_Body_Weight_kg,
    ROUND(AVG(Mean_Observed_Depth_m), 2)
        AS Mean_Taxon_Observed_Depth_m
FROM species_reference
GROUP BY
    IUCN_Status,
    IUCN_Risk_Score,
    Conservation_Group;

CREATE VIEW v_species_environment_profile AS
SELECT
    Scientific_Name,
    Common_Name,
    Class,
    Habitat_Type,
    Diet,
    IUCN_Status,
    Is_Threatened,
    Primary_Biome,
    Observation_Count,
    Location_Count,
    Depth_Min_m,
    Depth_Max_m,
    Mean_Observed_Depth_m,
    Mean_Water_Temp_C,
    Mean_Salinity_ppt,
    Mean_pH,
    Mean_Body_Length_cm,
    Mean_Body_Weight_kg,
    Mean_Estimated_Age_yr
FROM species_reference;

CREATE VIEW v_habitat_summary AS
SELECT
    Habitat_Type,
    COUNT(*) AS Taxon_Count,
    SUM(Observation_Count) AS Observation_Count,
    SUM(Is_Threatened) AS Threatened_Taxon_Count,
    ROUND(
        100.0 * SUM(Is_Threatened) / NULLIF(COUNT(*), 0),
        2
    ) AS Threatened_Taxon_Percentage,
    ROUND(AVG(Mean_Observed_Depth_m), 2)
        AS Mean_Taxon_Observed_Depth_m,
    ROUND(AVG(Mean_Water_Temp_C), 2)
        AS Mean_Taxon_Water_Temp_C
FROM species_reference
GROUP BY Habitat_Type;

CREATE VIEW v_annual_observation_trends AS
SELECT
    Observation_Year,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Observed_Taxon_Count,
    COUNT(DISTINCT Location) AS Location_Count,
    ROUND(AVG(Obs_Depth_m), 2) AS Mean_Observed_Depth_m,
    ROUND(AVG(Water_Temp_C), 2) AS Mean_Water_Temp_C,
    ROUND(AVG(Salinity_ppt), 2) AS Mean_Salinity_ppt,
    ROUND(AVG(pH), 3) AS Mean_pH
FROM observations
GROUP BY Observation_Year;

CREATE VIEW v_location_coverage AS
SELECT
    Location,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Observed_Taxon_Count,
    COUNT(DISTINCT Biome) AS Biome_Count,
    COUNT(DISTINCT Observation_Method) AS Method_Count,
    ROUND(AVG(Latitude), 4) AS Mean_Latitude,
    ROUND(AVG(Longitude), 4) AS Mean_Longitude,
    MIN(Observation_Date) AS First_Observation_Date,
    MAX(Observation_Date) AS Last_Observation_Date
FROM observations
GROUP BY Location;

CREATE VIEW v_observation_method_summary AS
SELECT
    Observation_Method,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Observed_Taxon_Count,
    COUNT(DISTINCT Location) AS Location_Count,
    MIN(Observation_Date) AS First_Observation_Date,
    MAX(Observation_Date) AS Last_Observation_Date
FROM observations
GROUP BY Observation_Method;
