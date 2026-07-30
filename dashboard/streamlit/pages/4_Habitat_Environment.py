import plotly.express as px
import streamlit as st

from utils import configure_page, header, load_csv, species_filters, style_figure

configure_page("Habitat & Environment", "🌡️")
header("Habitat & Environment", "Compare taxon-level environmental profiles.")
species = species_filters(load_csv("species.csv"), "environment")
habitats = load_csv("habitats.csv")
biomes = load_csv("biomes.csv")

left, right = st.columns(2)
with left:
    fig = px.scatter(
        species, x="Mean_Water_Temp_C", y="Mean_Observed_Depth_m",
        color="Habitat_Type", size="Mean_Body_Length_cm",
        hover_name="Common_Name", log_y=True,
        title="Temperature and observed depth",
        labels={
            "Mean_Water_Temp_C": "Mean water temperature (°C)",
            "Mean_Observed_Depth_m": "Mean observed depth (m)",
            "Habitat_Type": "Habitat",
            "Mean_Body_Length_cm": "Mean body length (cm)",
        },
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)
with right:
    fig = px.scatter(
        species, x="Mean_Salinity_ppt", y="Mean_pH",
        color="Habitat_Type", hover_name="Common_Name",
        title="Salinity and pH",
        labels={
            "Mean_Salinity_ppt": "Mean salinity (ppt)",
            "Mean_pH": "Mean pH",
            "Habitat_Type": "Habitat",
        },
    )
    st.plotly_chart(style_figure(fig), use_container_width=True)

fig = px.bar(
    habitats, x="Habitat_Type", y="Taxon_Count",
    color="Threatened_Taxon_Percentage",
    title="Habitat composition and threatened share",
    color_continuous_scale="OrRd",
    labels={
        "Habitat_Type": "Habitat",
        "Taxon_Count": "Taxa",
        "Threatened_Taxon_Percentage": "Threatened taxa (%)",
    },
)
st.plotly_chart(style_figure(fig), use_container_width=True)
st.subheader("Biome environmental summary")
st.dataframe(
    biomes.rename(columns={
        "Observation_Count": "Observations",
        "Taxon_Count": "Taxa",
        "Mean_Depth_m": "Mean depth (m)",
        "Mean_Temperature_C": "Mean temperature (°C)",
        "Mean_Salinity_ppt": "Mean salinity (ppt)",
        "Mean_pH": "Mean pH",
    }),
    use_container_width=True,
    hide_index=True,
)
