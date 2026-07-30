import plotly.express as px
import streamlit as st

from utils import (
    IUCN_COLORS, IUCN_ORDER, configure_page, download_csv, header, load_csv,
    no_data, species_filters, style_figure,
)

configure_page("Species Explorer", "🐟")
header("Species Explorer", "Filter and compare 101 full scientific-name taxa.")
species = species_filters(load_csv("species.csv"), "explorer")
no_data(species)

c1, c2, c3, c4 = st.columns(4)
c1.metric("Filtered taxa", len(species))
c2.metric("Classes", species["Class"].nunique())
c3.metric("Habitats", species["Habitat_Type"].nunique())
c4.metric("Threatened", int(species["Is_Threatened"].sum()))

fig = px.scatter(
    species, x="Mean_Body_Length_cm", y="Mean_Body_Weight_kg",
    color="IUCN_Status", size="Mean_Estimated_Age_yr", hover_name="Common_Name",
    hover_data=["Scientific_Name", "Class"],
    log_x=True, log_y=True, title="Taxon morphology",
    category_orders={"IUCN_Status": IUCN_ORDER},
    color_discrete_map=IUCN_COLORS,
    labels={
        "Mean_Body_Length_cm": "Mean body length (cm)",
        "Mean_Body_Weight_kg": "Mean body weight (kg)",
        "IUCN_Status": "IUCN status",
        "Mean_Estimated_Age_yr": "Mean estimated age (years)",
    },
)
st.plotly_chart(style_figure(fig, 520), use_container_width=True)

selected = st.selectbox("Species profile", species["Common_Name"].sort_values())
row = species.loc[species["Common_Name"] == selected].iloc[0]
st.subheader(f"{row.Common_Name} — *{row.Scientific_Name}*")
st.info(f"**IUCN status:** {row.IUCN_Status}")
cols = st.columns(4)
cols[0].metric("Mean length", f"{row.Mean_Body_Length_cm:,.1f} cm")
cols[1].metric("Mean weight", f"{row.Mean_Body_Weight_kg:,.2f} kg")
cols[2].metric("Mean depth", f"{row.Mean_Observed_Depth_m:,.1f} m")
cols[3].metric("Mean age", f"{row.Mean_Estimated_Age_yr:,.1f} yr")
st.write(row.Fun_Fact)
display_columns = [
    "Common_Name", "Scientific_Name", "Class", "Habitat_Type", "Diet",
    "IUCN_Status", "Mean_Body_Length_cm", "Mean_Body_Weight_kg",
    "Mean_Observed_Depth_m",
]
display_names = {
    "Common_Name": "Common name", "Scientific_Name": "Scientific name",
    "Habitat_Type": "Habitat", "IUCN_Status": "IUCN status",
    "Mean_Body_Length_cm": "Mean length (cm)",
    "Mean_Body_Weight_kg": "Mean weight (kg)",
    "Mean_Observed_Depth_m": "Mean depth (m)",
}
st.dataframe(
    species[display_columns].rename(columns=display_names),
    use_container_width=True, hide_index=True,
)
download_csv(species, "Download filtered taxa", "filtered_species.csv")
