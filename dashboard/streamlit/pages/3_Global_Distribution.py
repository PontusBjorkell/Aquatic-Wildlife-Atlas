import plotly.express as px
import numpy as np
import streamlit as st

from utils import caveat, configure_page, header, load_csv, style_figure

configure_page("Global Distribution", "🗺️")
header("Global Distribution", "Explore a deterministic 25,000-record coordinate sample.")
caveat()
data = load_csv("map_sample.csv")
locations = load_csv("locations.csv")

c1, c2, c3 = st.columns(3)
habitats = c1.multiselect("Habitat", sorted(data.Habitat_Type.unique()))
statuses = c2.multiselect("IUCN status", sorted(data.IUCN_Status.unique()))
years = c3.slider(
    "Observation year", int(data.Observation_Year.min()),
    int(data.Observation_Year.max()),
    (int(data.Observation_Year.min()), int(data.Observation_Year.max())),
)
filtered = data[data.Observation_Year.between(*years)]
if habitats:
    filtered = filtered[filtered.Habitat_Type.isin(habitats)]
if statuses:
    filtered = filtered[filtered.IUCN_Status.isin(statuses)]

display_limit = 8_000
step = max(1, int(np.ceil(len(filtered) / display_limit)))
display = filtered.iloc[::step].head(display_limit)
fig = px.scatter_geo(
    display, lat="Latitude", lon="Longitude", color="Habitat_Type",
    hover_name="Common_Name", hover_data=["Location", "IUCN_Status", "Biome"],
    opacity=0.28, projection="natural earth",
    title=f"Mapped display sample ({len(display):,} of {len(filtered):,} filtered records)",
    labels={"Habitat_Type": "Habitat", "IUCN_Status": "IUCN status"},
)
fig.update_traces(marker={"size": 3})
st.plotly_chart(style_figure(fig, 620), use_container_width=True)
st.warning(
    "Named locations and coordinates are not consistently aligned. "
    "The map is a data-quality diagnostic, not a verified occurrence map."
)
st.subheader("Named-location coverage")
st.dataframe(
    locations.rename(columns={
        "Observation_Count": "Observations",
        "Observed_Taxon_Count": "Observed taxa",
        "Biome_Count": "Biomes",
        "Method_Count": "Methods",
        "Mean_Latitude": "Mean latitude",
        "Mean_Longitude": "Mean longitude",
        "First_Observation_Date": "First observation",
        "Last_Observation_Date": "Last observation",
    }),
    use_container_width=True,
    hide_index=True,
)
