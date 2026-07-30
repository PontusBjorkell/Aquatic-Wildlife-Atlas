-- Named SQL catalogue for Aquatic Wildlife Atlas.
-- Each query begins with "-- name:" so the Python runner can export it.

-- name: 01_executive_summary
SELECT
    (SELECT COUNT(*) FROM observations) AS Observation_Count,
    (SELECT COUNT(*) FROM species_reference) AS Taxon_Count,
    (SELECT COUNT(DISTINCT Class) FROM species_reference) AS Class_Count,
    (SELECT COUNT(DISTINCT Habitat_Type) FROM species_reference)
        AS Habitat_Count,
    (SELECT COUNT(DISTINCT Location) FROM observations) AS Location_Count,
    (SELECT COUNT(DISTINCT Biome) FROM observations) AS Biome_Count,
    (SELECT COUNT(*) FROM species_reference WHERE Is_Threatened = 1)
        AS Threatened_Taxon_Count,
    (SELECT MIN(Observation_Date) FROM observations)
        AS First_Observation_Date,
    (SELECT MAX(Observation_Date) FROM observations)
        AS Last_Observation_Date;

-- name: 02_taxonomy_by_phylum
SELECT
    Phylum,
    COUNT(*) AS Taxon_Count,
    SUM(Observation_Count) AS Observation_Count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
        AS Taxon_Percentage
FROM species_reference
GROUP BY Phylum
ORDER BY Taxon_Count DESC, Phylum;

-- name: 03_taxonomy_by_class
SELECT
    Class,
    COUNT(*) AS Taxon_Count,
    COUNT(DISTINCT "Order") AS Order_Count,
    COUNT(DISTINCT Family) AS Family_Count,
    SUM(Observation_Count) AS Observation_Count
FROM species_reference
GROUP BY Class
ORDER BY Taxon_Count DESC, Class;

-- name: 04_taxonomy_by_order
SELECT
    Class,
    "Order" AS Taxonomic_Order,
    COUNT(*) AS Taxon_Count,
    COUNT(DISTINCT Family) AS Family_Count
FROM species_reference
GROUP BY Class, "Order"
ORDER BY Taxon_Count DESC, Class, Taxonomic_Order;

-- name: 05_family_diversity
SELECT
    Family,
    Class,
    COUNT(*) AS Taxon_Count,
    COUNT(DISTINCT Genus) AS Genus_Count,
    SUM(Observation_Count) AS Observation_Count
FROM species_reference
GROUP BY Family, Class
ORDER BY Taxon_Count DESC, Family;

-- name: 06_conservation_status_summary
SELECT *
FROM v_conservation_summary
ORDER BY IUCN_Risk_Score;

-- name: 07_threatened_taxa
SELECT
    Common_Name,
    Scientific_Name,
    Class,
    Habitat_Type,
    Primary_Biome,
    IUCN_Status,
    IUCN_Risk_Score,
    Observation_Count
FROM species_reference
WHERE Is_Threatened = 1
ORDER BY IUCN_Risk_Score DESC, Common_Name;

-- name: 08_threatened_taxa_by_class
SELECT
    Class,
    COUNT(*) AS Taxon_Count,
    SUM(Is_Threatened) AS Threatened_Taxon_Count,
    ROUND(
        100.0 * SUM(Is_Threatened) / NULLIF(COUNT(*), 0),
        2
    ) AS Threatened_Taxon_Percentage
FROM species_reference
GROUP BY Class
ORDER BY Threatened_Taxon_Percentage DESC, Taxon_Count DESC, Class;

-- name: 09_threatened_taxa_by_habitat
SELECT *
FROM v_habitat_summary
ORDER BY Threatened_Taxon_Percentage DESC, Taxon_Count DESC;

-- name: 10_conservation_risk_ranking
SELECT
    Common_Name,
    Scientific_Name,
    Class,
    Habitat_Type,
    IUCN_Status,
    IUCN_Risk_Score,
    Mean_Body_Length_cm,
    Mean_Observed_Depth_m,
    Location_Count
FROM species_reference
ORDER BY
    IUCN_Risk_Score DESC,
    Location_Count ASC,
    Common_Name;

-- name: 11_habitat_composition
SELECT
    Habitat_Type,
    COUNT(*) AS Taxon_Count,
    SUM(Observation_Count) AS Observation_Count,
    COUNT(DISTINCT Class) AS Class_Count,
    ROUND(AVG(Mean_Water_Temp_C), 2) AS Mean_Taxon_Temperature_C,
    ROUND(AVG(Mean_Observed_Depth_m), 2) AS Mean_Taxon_Depth_m
FROM species_reference
GROUP BY Habitat_Type
ORDER BY Taxon_Count DESC, Habitat_Type;

-- name: 12_biome_composition
SELECT
    Primary_Biome AS Biome,
    COUNT(*) AS Taxon_Count,
    SUM(Observation_Count) AS Observation_Count,
    SUM(Is_Threatened) AS Threatened_Taxon_Count,
    ROUND(AVG(Mean_Water_Temp_C), 2) AS Mean_Taxon_Temperature_C
FROM species_reference
GROUP BY Primary_Biome
ORDER BY Taxon_Count DESC, Biome;

-- name: 13_diet_composition
SELECT
    Diet,
    COUNT(*) AS Taxon_Count,
    SUM(Is_Threatened) AS Threatened_Taxon_Count,
    ROUND(AVG(Mean_Body_Length_cm), 2) AS Mean_Taxon_Length_cm,
    ROUND(AVG(Mean_Body_Weight_kg), 2) AS Mean_Taxon_Weight_kg
FROM species_reference
GROUP BY Diet
ORDER BY Taxon_Count DESC, Diet;

-- name: 14_habitat_conservation_matrix
SELECT
    Habitat_Type,
    IUCN_Status,
    IUCN_Risk_Score,
    COUNT(*) AS Taxon_Count
FROM species_reference
GROUP BY Habitat_Type, IUCN_Status, IUCN_Risk_Score
ORDER BY Habitat_Type, IUCN_Risk_Score;

-- name: 15_class_habitat_matrix
SELECT
    Class,
    Habitat_Type,
    COUNT(*) AS Taxon_Count
FROM species_reference
GROUP BY Class, Habitat_Type
ORDER BY Taxon_Count DESC, Class, Habitat_Type;

-- name: 16_depth_band_summary
SELECT
    Depth_Band,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Observed_Taxon_Count,
    ROUND(AVG(Water_Temp_C), 2) AS Mean_Water_Temp_C,
    ROUND(AVG(Salinity_ppt), 2) AS Mean_Salinity_ppt,
    ROUND(AVG(pH), 3) AS Mean_pH
FROM observations
GROUP BY Depth_Band
ORDER BY MIN(Obs_Depth_m);

-- name: 17_deepest_taxa
SELECT
    Common_Name,
    Scientific_Name,
    Class,
    Habitat_Type,
    Depth_Min_m,
    Depth_Max_m,
    Mean_Observed_Depth_m
FROM species_reference
ORDER BY Depth_Max_m DESC, Mean_Observed_Depth_m DESC
LIMIT 25;

-- name: 18_largest_taxa_by_length
SELECT
    Common_Name,
    Scientific_Name,
    Class,
    Diet,
    IUCN_Status,
    ROUND(Mean_Body_Length_cm, 2) AS Mean_Body_Length_cm,
    ROUND(Median_Body_Length_cm, 2) AS Median_Body_Length_cm
FROM species_reference
ORDER BY Mean_Body_Length_cm DESC
LIMIT 25;

-- name: 19_heaviest_taxa
SELECT
    Common_Name,
    Scientific_Name,
    Class,
    Diet,
    IUCN_Status,
    ROUND(Mean_Body_Weight_kg, 3) AS Mean_Body_Weight_kg,
    ROUND(Median_Body_Weight_kg, 3) AS Median_Body_Weight_kg
FROM species_reference
ORDER BY Mean_Body_Weight_kg DESC
LIMIT 25;

-- name: 20_longest_lived_taxa
SELECT
    Common_Name,
    Scientific_Name,
    Class,
    Habitat_Type,
    IUCN_Status,
    ROUND(Mean_Estimated_Age_yr, 2) AS Mean_Estimated_Age_yr
FROM species_reference
ORDER BY Mean_Estimated_Age_yr DESC
LIMIT 25;

-- name: 21_species_morphology_profile
SELECT
    Common_Name,
    Scientific_Name,
    Class,
    Diet,
    ROUND(Mean_Body_Length_cm, 2) AS Mean_Body_Length_cm,
    ROUND(Mean_Body_Weight_kg, 3) AS Mean_Body_Weight_kg,
    ROUND(Mean_Estimated_Age_yr, 2) AS Mean_Estimated_Age_yr
FROM species_reference
ORDER BY Class, Common_Name;

-- name: 22_environment_by_habitat
SELECT
    Habitat_Type,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Taxon_Count,
    ROUND(AVG(Obs_Depth_m), 2) AS Mean_Depth_m,
    ROUND(AVG(Water_Temp_C), 2) AS Mean_Temperature_C,
    ROUND(AVG(Salinity_ppt), 2) AS Mean_Salinity_ppt,
    ROUND(AVG(pH), 3) AS Mean_pH
FROM observations
GROUP BY Habitat_Type
ORDER BY Observation_Count DESC;

-- name: 23_environment_by_biome
SELECT
    Biome,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Taxon_Count,
    ROUND(AVG(Obs_Depth_m), 2) AS Mean_Depth_m,
    ROUND(AVG(Water_Temp_C), 2) AS Mean_Temperature_C,
    ROUND(AVG(Salinity_ppt), 2) AS Mean_Salinity_ppt,
    ROUND(AVG(pH), 3) AS Mean_pH
FROM observations
GROUP BY Biome
ORDER BY Observation_Count DESC;

-- name: 24_salinity_extremes_by_taxon
SELECT
    Common_Name,
    Scientific_Name,
    Habitat_Type,
    Primary_Biome,
    ROUND(Mean_Salinity_ppt, 2) AS Mean_Salinity_ppt
FROM species_reference
ORDER BY Mean_Salinity_ppt DESC;

-- name: 25_temperature_extremes_by_taxon
SELECT
    Common_Name,
    Scientific_Name,
    Habitat_Type,
    Primary_Biome,
    ROUND(Mean_Water_Temp_C, 2) AS Mean_Water_Temp_C
FROM species_reference
ORDER BY Mean_Water_Temp_C DESC;

-- name: 26_location_coverage
SELECT *
FROM v_location_coverage
ORDER BY Observation_Count DESC, Location;

-- name: 27_taxon_geographic_breadth
SELECT
    Common_Name,
    Scientific_Name,
    Class,
    Habitat_Type,
    Location_Count,
    Observation_Count,
    First_Observation_Date,
    Last_Observation_Date
FROM species_reference
ORDER BY Location_Count DESC, Common_Name;

-- name: 28_observation_method_summary
SELECT *
FROM v_observation_method_summary
ORDER BY Observation_Count DESC, Observation_Method;

-- name: 29_annual_observation_trends
SELECT *,
    ROUND(
        100.0 * (
            Observation_Count
            - LAG(Observation_Count) OVER (ORDER BY Observation_Year)
        )
        / NULLIF(
            LAG(Observation_Count) OVER (ORDER BY Observation_Year),
            0
        ),
        2
    ) AS Year_Over_Year_Change_Percentage
FROM v_annual_observation_trends
ORDER BY Observation_Year;

-- name: 30_monthly_seasonality
SELECT
    Observation_Month,
    Observation_Month_Name,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Observed_Taxon_Count,
    ROUND(AVG(Water_Temp_C), 2) AS Mean_Water_Temp_C
FROM observations
GROUP BY Observation_Month, Observation_Month_Name
ORDER BY Observation_Month;

-- name: 31_sex_distribution
SELECT
    Sex,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Observed_Taxon_Count,
    ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (), 2)
        AS Observation_Percentage
FROM observations
GROUP BY Sex
ORDER BY Observation_Count DESC, Sex;

-- name: 32_observation_method_by_habitat
SELECT
    Habitat_Type,
    Observation_Method,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Taxon_ID) AS Observed_Taxon_Count
FROM observations
GROUP BY Habitat_Type, Observation_Method
ORDER BY Habitat_Type, Observation_Count DESC;

-- name: 33_coordinate_dispersion_by_location
SELECT
    Location,
    COUNT(*) AS Observation_Count,
    ROUND(MIN(Latitude), 3) AS Min_Latitude,
    ROUND(MAX(Latitude), 3) AS Max_Latitude,
    ROUND(MAX(Latitude) - MIN(Latitude), 3) AS Latitude_Span,
    ROUND(MIN(Longitude), 3) AS Min_Longitude,
    ROUND(MAX(Longitude), 3) AS Max_Longitude,
    ROUND(MAX(Longitude) - MIN(Longitude), 3) AS Longitude_Span
FROM observations
GROUP BY Location
ORDER BY Longitude_Span DESC, Latitude_Span DESC;

-- name: 34_taxon_observation_balance
SELECT
    MIN(Observation_Count) AS Minimum_Observations_Per_Taxon,
    MAX(Observation_Count) AS Maximum_Observations_Per_Taxon,
    ROUND(AVG(Observation_Count), 2) AS Mean_Observations_Per_Taxon,
    MAX(Observation_Count) - MIN(Observation_Count)
        AS Max_Min_Difference,
    COUNT(*) AS Taxon_Count
FROM species_reference;

-- name: 35_template_attribute_constancy
SELECT
    Scientific_Name,
    Common_Name,
    COUNT(*) AS Observation_Count,
    COUNT(DISTINCT Depth_Min_m) AS Distinct_Depth_Min_Values,
    COUNT(DISTINCT Depth_Max_m) AS Distinct_Depth_Max_Values,
    COUNT(DISTINCT Habitat_Type) AS Distinct_Habitat_Values,
    COUNT(DISTINCT Diet) AS Distinct_Diet_Values,
    COUNT(DISTINCT IUCN_Status) AS Distinct_IUCN_Values,
    COUNT(DISTINCT Biome) AS Distinct_Biome_Values,
    COUNT(DISTINCT Fun_Fact) AS Distinct_Fun_Facts
FROM observations
GROUP BY Scientific_Name, Common_Name
ORDER BY Scientific_Name;
